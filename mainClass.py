#to make http requests
import requests
#to parse html
from lxml import html
#for date and time
import time
import datetime
#for extracting media
from bs4 import BeautifulSoup
#for opening the html page
import urllib
#to make directories
import os
#import shutil for download
import shutil
#for creating deepcopy of mutable objects
import copy
#for regular expressions
import re
#for output
import json
import csv
#for flattening json
from flatten_json import flatten

#self made library
import loader

#*****************************************************************setting all the global variables*******************************************************************
#setting up request headers most likely apple mobile
REQUEST_HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36'}

#set up manfacturer name
MANUFACTURER = 'Snapper'

#country list has only one item in it
COUNTRIES = ['US']

#set up categories mapping
CATEGORY_MAPPING = {
    0: 'category',
    1: 'subcategory',
    2: 'subsubcategory',
    3: 'subsubsubcategory'
}

#set up label category mapping
LABEL_CATEGORY_MAPPING = {
    'productTitle': 'general',
    'desc': 'general',
    'accessories': 'general'
}

PRODUCT_LINK_EXCEPTIONS = [
    '/na/en_us/products/snapper-xd-82v-max/xd-82v-max-string-trimmer-attachments.html',
    '/na/en_us/products/snapper-xd-82v-max/xd-82v-product-bundles.html'
]
EXCEL_SORT_LIST = ['general', 'specification', 'option', 'feature', 'brochure', 'image']
IMG_EXCEPTIONS = ['bascob2c', 'Logos', 'Icons', '#']
SPEC_EXCEPTIONS = ["Operator's Manual - English, Spanish, French", "Operator's Manuals"]
SPECS_TO_BE_PUT_IN_GENERAL = {
    'US MAP (Minimum Advertised Price) ^': 'msrp',
    'US MAP (Minimum Advertised Price)^': 'msrp',
    'CAN MAP (Minimum Advertised Price)': 'msrpCAN',
    'CAN MAP (Minimum Advertised Price)^': 'msrpCAN',
    'Model': 'model'
}
FILE_EXTENSIONS = {
    'src': '.jpg',
    'attachmentUrl': '.pdf'
}

DIRECTORIES_LIST = ['Images', 'PDFs']

#******************************************************************** end of global variables **********************************************************************

#this is the class for scraping the website
class scrapper:
    #constructor
    def __init__(self,url,purl,cat_xpath,prod_xpath,prod_info,allow_download,spec_names,json_output,csv_output):
        #first data member is the products url that will be loaded from the yaml file
        self.products_url = purl
        self.backup_products_url= purl

        #set the main url which will be used for later purposes
        self.main_url = url

        #create category_xpath_list and product_xpath_string
        self.category_xpath_list = cat_xpath
        self.product_xpath_string = prod_xpath

        #this is also required
        self.product_info = prod_info
        self.allow_download = allow_download
        self.spec_names = spec_names
        
        #create categorylinks and product links
        self.category_links = list()
        self.product_links = list()

        #create output destinations
        self.json_output = json_output
        self.csv_output = csv_output

    #to make a get reuest to the specified url
    def get_request(self):
        #got the response
        response = requests.get(self.products_url)
        return response

    #to create an html tree out of the response
    #we will need to use html imported from lxml library
    def html_parser(self,html_value):
        return html.fromstring(html_value)

    #url builder method
    def build_url(self,partial_url):
        #return the argument value if it starts with http otherwise return params['url']+partial_url which is equal to https://snapper.com + partial_url
        #params is the variable created from params.yaml file loaded at the start of the code
        #if you go there then you can see that the url parameter is https://snapper.com
        return partial_url if partial_url.startswith('http') else self.main_url + partial_url
    
    #this will get all the product links and category list values
    def get_product_links(self,htmltree,category_xpath_list,product_xpath_string):
        #as we now know that params['links'] gives us a list whereas params['product'] gives us a string
        #so to store category links that comes from params['links'] we create a list
        category_links = list()

        #if category_xpath_list is an instance or subclass of list class, which it is then
        if isinstance(category_xpath_list, list):
            #now for each item that is each link in category_xpath_list we will get the whole list of values and assign append them in cat_links
            for item in category_xpath_list:
                category_links.extend(htmltree.xpath(item))

            return category_links, htmltree.xpath(product_xpath_string)

    #now the entire test1 phase will be converted to a method called greedy scrape
    def greedy_scrape(self):
        #print(self.products_url)
        #get response by making http get request to the first assigned products url
        resp = self.get_request()

        #create an html tree out of resp.content
        htmltree = self.html_parser(resp.content)

        #get cateegory links and product links from webpage
        category_links,product_links = self.get_product_links(htmltree,self.category_xpath_list,self.product_xpath_string)

        #test print
        #print(category_links)
        #print(product_links)

        #now assign these values to the category link and product link data members after some operations
        if product_links:
            self.product_links.extend(product_links)

        if category_links:
            self.category_links.extend(category_links)
            #print("The category links got on this url:")
            #print(self.category_links)

        if self.category_links:
            #now for each item in the category list that has been retrieved assign it to cat
            for cat in self.category_links:
                #remove it from the list
                self.category_links.remove(cat)
                #print("After removing cat from it:")
                #print(self.category_links)
                #assign it to self.products_url by building it using self.build_url
                self.products_url = self.build_url(cat)
                #call self.greedy_scrape() again
                #print(self.category_links)
                #print(self.product_links)
                self.greedy_scrape()


        #HOW IT WORKS:-
                #say it has links: - a,b
                #first a will be assigned to cat and removed fromt he list
                #then when the method recurs,
                    #a request will be made to a and an htmltree will be made out of which category_lists- e,f will be found and addded
                #now e will be assigned to cat and removed from the list
                    #a request will be made to e and an htmltree will be made out of which no category url was found. So list is empty nothing happens
                #now f will be assigned to cat and removed from the list
                    #a request will be made to f and an htmltree will be made out of which no category url was found. So list is empty nothing happens
                #now b will be assigned to cat and removed from the list
                    #a request will be made to b and an htmltree will be made out of which no category url was found. So list is empty nothing happens

        #finally a list of all the product urls will be made and category list will be empty

        #also assign self.products_url to its default value
        self.products_url = self.backup_products_url
        #print(self.products_url)

        #basically we got a whole pool of product urls from category urls


    #for each item in the list provided to us, it will replace text to replace which will be an arg with replace text whcihc will
    #also be an arg. By default, both of their values will be ''
    def str_replace(self,string_list, text_to_replace='', replacement_text=''):
        for item in range(len(string_list)):
            string_list[item] = string_list[item].replace(text_to_replace, replacement_text)
        #finally return the list
        return string_list
        
    def list_sanitizer(self,list_to_be_sanitized):
        #calling str_replace(list,toreplace='',replace='')
        #since the value of the last two parameters are already predefined, it is optional to provide arguments for them
        #here only the string_list is being sent so nothing will be replaced.
        #the whole string will be returned back.

        #WHAT WILL BE IN THE STRING:
        #- if no character arguement is provided to str.strip method, it will look for blankspaces
        #- so for all items as words in list_to_be_sanitized which is the parameter here,
            #if word.rstrip exists that is if it is not a blankspace
            #a value stripped of blank spaces on both of its sides will be created
        #the array will contain these values and will be passed to str_replace which will return it as it is since the last two args are not given
        return self.str_replace([word.strip() for word in list_to_be_sanitized if word.rstrip()])

    #return a list of specifications where each item in a list is a dictionary
    def get_specs(self,spec_elements):
        #print(spec_elements)
        #the spec_elements are a list of xpath elements formed from the html tree
        spec_dict = dict()
        spec_list = list()

        for item in spec_elements:
            #now for every xpath element we get the text content and strip it of whitespaces
            spec = item.text_content().strip()
            #print(spec)
            #now we sanitize the stripped text contents stored in spec using self.list_sanitizer
            spec2 = self.list_sanitizer(spec.splitlines())
            #thus the spec will be converted to a list and assigned to spec2 where the first element of every item in spec2 will be the key value
            #print(spec2)

            if spec2[0] in SPEC_EXCEPTIONS:
                continue

            if spec2[0] == 'Model':
                #if spec_dict is not empty, which it will be at first, then after the zip method works it wont be empty
                if spec_dict:
                    #this will give us dictionaries that are formed
                    #print(spec_dict)

                    #this will create a list out of the dictionaries
                    spec_list.append(spec_dict)

                #then again we will empty the dictionary so that things wont be appended and the dictionary is fresh   
                spec_dict = dict()
                
            #this will update sepc_dict
            #the zip function acts like respectively does in math. spec2[0:n:gap=2] and spec2[1:n:gap=2] will be assigned as pairs in a dictionary and be updated in spec_dict
            spec_dict.update(dict(zip(spec2[::2], spec2[1::2])))

        #finally this one is for the last dictionary element
        spec_list.append(spec_dict)
        return spec_list

    #return a list of categories
    def get_categories(self,category_elements):
        category_list = list()
        cat_list = dict()
        breadcrumb_exceptions = ['Home', 'Products']

        for item in category_elements:
            category_list.extend(self.list_sanitizer(item.text_content().strip().splitlines()))

        if category_list:
            category_list = [item for item in category_list if item not in breadcrumb_exceptions]

        for x in range(len(category_list)):
            cat_list[CATEGORY_MAPPING[x]] = category_list[x]

        return cat_list

    #a function that will makes directories if they do not exist already
    def make_directories(self):
        for directory in DIRECTORIES_LIST:
            #here Images and PDFs directories will be created
            if not os.path.exists(directory):
                os.makedirs(directory)
                
    #to download media
    def download_media(self,url_list, directory, link_name):
        #the directories pdf and images will be made if they alreadt do not exist
        self.make_directories()

        #then for each value in the parameter url_list as url
        for url in url_list:
            #if url has title then use url['title']+ FILE_EXTENSIONS[linkname(this is a parameter)] else use url[link_name] and split it of '/' from the right side and take the last element
            filename = url['title'] + FILE_EXTENSIONS[link_name] if 'title' in url else url[link_name].rsplit('/', 1)[-1]
            #replace all '/' with ' '
            filename = filename.replace('/', ' ')
            i = 1
            #os.path.isfile(path): Return True if path is an existing regular file. This follows symbolic links, so both islink() and isfile() can be true for the same path.
            while os.path.isfile(directory + '/' + filename):
                #if this is the first iteration in the loop
                if i == 1:
                    #set filename = filename(1)
                    filename = filename + ' (' + str(i) + ')'
                else:
                    #otherwise replace the previous (i) with the new (i)
                    filename = filename.replace(' (' + str(i - 1) + ')', ' (' + str(i) + ')')
                #increment i
                i = i + 1

            #get url[link_name] as response and write to directory/filename i.e out_file
            with urllib.request.urlopen(url[link_name]) as response, open(directory + '/' + filename, 'wb') as out_file:
                #main download command
                shutil.copyfileobj(response, out_file)
    
    #to extract images, videos and pdfs
    def extract_media(self,response):
        #make a list of images, videos and pdfs
        img_list = list()
        vid_list = list()
        pdf_list = list()

        #now create soup out of response and find all images, a and iframe tags
        soup = BeautifulSoup(response.content, 'html.parser')
        img_tags = soup.find_all('img')
        vid_tags = soup.find_all('iframe')
        a_tags = soup.find_all('a')

        #now for each item in a tag
        for a in a_tags:
            #print(a) => gave us all the a tags
            if a.has_attr('model'):
                #print(a['model'])
                pdf_list.append({'attachmentName': a.text.strip(), 'model': a['model'], 'attachmentUrl': self.build_url(a['href'])})

        #for each item in vid_tags
        for vid in vid_tags:
            #if vid has src attribute and that source attribute has youtube in it
            if vid.has_attr('src') and 'youtube' in vid['src']:
                #print(vid['src'])
                vid_list.append({'src': vid['src'] if vid['src'].startswith('http') else 'http:' + vid['src']})

        #for each item in img_tags
        for img in img_tags:
            #if any of the x in IMG_EXCEPTIONS is in str(img) then do not proceed any further 
            if any(x in str(img) for x in IMG_EXCEPTIONS):
                continue

            #if any IMG_EXCEPTIONS items are not in img but img does not have src attribute then do nothing
            if not img.has_attr('src'):
                continue

            #if nay IMG_EXCETIONS items are not in img and img has src attribute then
            #if img also has title then  
            if img.has_attr('title'):
                #append desc and src to img_list
                img_list.append({'desc': img['title'], 'src': self.build_url(img['src'])})
            else:
                #append src to img_list
                img_list.append({'src': self.build_url(img['src'])})

        if self.allow_download:
            self.download_media(img_list, 'Images', 'src')
            self.download_media(pdf_list, 'PDFs', 'attachmentUrl')

        return img_list, vid_list, pdf_list       

    #
    def process_specs(self,product_spec):
        #create a new empty dictionary called specs
        specs = dict()

        #for key, val in product_spec.items()
        for key, val in product_spec.items():
            #if key is one of the self.spec_names.keys()
            if key in self.spec_names.keys():
                #if category field is not in specs then
                if self.spec_names[key]['category'] not in specs:
                    #create a field of category
                    specs[self.spec_names[key]['category']] = dict()
                #then update the value
                specs[self.spec_names[key]['category']][self.spec_names[key]['name']] = {'label': key, 'desc': val}
            else:
                #if key is not in self.spec_names.keys()
                if 'other' not in specs:
                    #if other filed is also not in specs then create the field
                    specs['other'] = dict()
                    #store it in other
                specs['other'].update({key: {'label': key, 'desc': val}})
        #return specs dictionary
        return specs
    
    #to give a final_scrape list
    def post_processing(self,scraped_data):
        #create finalscrape list and pdf list
        final_scrape = list()
        pdfs = list()

        #if scraped_data has 'pdfs' key
        if 'pdfs' in scraped_data:
            #then assign it to pdfs list 
            pdfs = scraped_data['pdfs']
            #and remove it from scraped_data
            del scraped_data['pdfs']

        #if scraped_data['specifications'] is a list
        if isinstance(scraped_data['specifications'], list):
            #for each item in scraped_data['specifications'] as product_spec
            for product_spec in scraped_data['specifications']:
                #For collections that are mutable or contain mutable items, a copy is sometimes needed so one can change one copy without changing the other.
                #there are two ways to keep a copy. Deep copy and shallow copy
                #Deep Copy: In case of deep copy, a copy of object is copied in other object.
                    #It means that any changes made to a copy of object do not reflect in the original object.
                    #In python, this is implemented using “deepcopy()” function.
                #Shallow Copy: In case of shallow copy, a reference of object is copied in other object.
                    #It means that any changes made to a copy of object do reflect in the original object.
                    #In python, this is implemented using “copy()” function.

                #here we have used deepcopy so that any changes made in the copy is not reflected in the original 
                new_prod = copy.deepcopy(scraped_data)

                #for each item in pdfs list as attachmentUrl
                for attachmentUrl in pdfs:
                    #if product_spec['Model'] is in attachmentUrl['model'], then
                    #NOTE: product_spec is an item in scraped_data['specifications'] from where this loop started
                    if product_spec['Model'] in attachmentUrl['model']:
                        #if new_prod does not have an attribute called attachments then
                        if 'attachments' not in new_prod:
                            #create a new attachment field and append some value to it
                            new_prod['attachments'] = list()
                        #if it already exists then simply append the value to it    
                        new_prod['attachments'].append({'attachmentUrl': attachmentUrl['attachmentUrl'], 'attachmentName': attachmentUrl['attachmentName']})

                #for each item in an intersection list of product_spec and SPECS_TO_BE_PUT_IN_GENERAL
                for item in set(product_spec).intersection(set(SPECS_TO_BE_PUT_IN_GENERAL)):
                    #if SPECS_TO_BE_PUT_IN_GENERAL[item] is msrp or msrpCAN
                    if SPECS_TO_BE_PUT_IN_GENERAL[item] == 'msrp' or SPECS_TO_BE_PUT_IN_GENERAL[item] == 'msrpCAN':
                        #create a new field in new_prod with the key general:{'msrp or msrpCAN: all items in product_spec[item] with the regex pattern found replaced by ''}'}
                        new_prod['general'].update({SPECS_TO_BE_PUT_IN_GENERAL[item]: re.sub("[^0-9|.]", "", product_spec[item])})
                    else:
                        #otherwise the new field should have product_spec[item]
                        new_prod['general'].update({SPECS_TO_BE_PUT_IN_GENERAL[item] : product_spec[item]})
                    #and after it has been assigned we will remove it from product_spec
                    del product_spec[item]

                #and after the whole thing is done we will delete the field of new_prod['specififcations'] as we dont need it anymore
                del new_prod['specifications']

                #we will then update the new_prod dicitonary with the method self.process_specs(product_spec) which is the item of the first loop in this method
                #this method will give us spec dictionary which will be a added to new_prod dictionary
                new_prod.update(self.process_specs(product_spec))
                #after the new_prod value is updated we will append it to final_scrape list
                final_scrape.append(new_prod)
        #at last return the final_scrape list
        return final_scrape

    
    def format_final_result(self,result):
        REQUIRED_RESULT_KEYS = ['videos', 'operational', 'engineAndDriveTrain', 'dimensions', 'other', 'images', 'features',
                            'options', 'attachments']
        REQUIRED_GENERAL_KEYS = ['manufacturer', 'model', 'year', 'msrp', 'category', 'subcategory', 'subsubcategory',
                                 'description', 'countries', 'extractedDate']
        REQUIRED_IMAGE_KEYS = ['src', 'desc', 'longDesc']
        REQUIRED_ATTACHMENT_KEYS = ['attachmentName', 'attachmentUrl', 'attachmentDescription']

        for res in result:
            res.update({key: None for key in res.keys() if not res[key]})
            res.update(self.make_dict_for_missing_keys(self.find_missing_keys(REQUIRED_RESULT_KEYS, res.keys())))
            res['general'].update(self.make_dict_for_missing_keys(self.find_missing_keys(REQUIRED_GENERAL_KEYS, res['general'].keys())))
            res['images'] = self.format_media(res['images'], REQUIRED_IMAGE_KEYS)
            res['videos'] = self.format_media(res['videos'], REQUIRED_IMAGE_KEYS)
            res['attachments'] = self.format_media(res['attachments'], REQUIRED_ATTACHMENT_KEYS)
            res['general']['subcategory'] = res['general']['subcategory'] if res['general']['subcategory'] else res['general']['category']

        return result

    def format_media(self,media_list, required_keys):
        if media_list:
            for item in media_list:
                item.update(self.make_dict_for_missing_keys(self.find_missing_keys(required_keys, item.keys())))
        return media_list


    def make_dict_for_missing_keys(self,missing_keys):
        return {missing_key: None for missing_key in missing_keys}


    def find_missing_keys(self,required_keys, result_keys):
        return list(set(required_keys) - set(result_keys))
    
    #method to get actual data from the product links got from seld.greedy_scrape()
    def get_product_info(self):
        final_scrape = list()

        #for each item in self.products_links
        for x in self.product_links:
            #if x is in PRODUCT_EXCEPTIONS THEN DO NOTHING
            if x in PRODUCT_LINK_EXCEPTIONS:
                #do not proceed any further and continue the loop, these are exceptions
                continue

            #the rest of the loop

            #else
            #get a valid url from self.build_url    

            self.products_url = self.build_url(x)

            #now get htmltree and response.content
            response = self.get_request()
            htmltree = self.html_parser(response.content)

            #print for test
            #print(response)
            #print(htmltree)

            scraped_data = {
                'productUri': self.products_url,
                'general': {
                    'extractedDate': datetime.datetime.now().isoformat(),
                    'year': str(datetime.datetime.now().year),
                    'countries': COUNTRIES,
                    'manufacturer': MANUFACTURER
                }
            }

            #iterate over json using key value pair
            #use params['product_info'] here
            for key, value in self.product_info.items(): 
                #for specs key -> add a new field called specification in scraped_data variable and assign 
                if key == 'specs':
                    scraped_data['specifications'] = self.get_specs(htmltree.xpath(value))
                elif key == 'categories':
                    scraped_data['general'].update(self.get_categories(htmltree.xpath(value)))
                    #print(scraped_data)
                elif key == 'description':
                    scraped_data['general']['description'] = ' '.join(self.list_sanitizer(htmltree.xpath(value)))
                    #print(scraped_data)
                else:
                    #now if the key that we recieve is one of the keys of LABEL_CATEGORY_MAPPINGs .e. productTitle, desc or accessories then 
                    if key in LABEL_CATEGORY_MAPPING.keys():
                        #since it is a part of LABEL_CATEGORY_MAPPING,
                        #check if the value of this key in LABLE_CATEGORY_MAPPING i.e LABEL_CATEGORY_MAPPING[key] is already in scraped data or not
                        if LABEL_CATEGORY_MAPPING[key] not in scraped_data:
                           #if not then create a new dictionary field and then update the corrsponding value
                           scraped_data[LABEL_CATEGORY_MAPPING[key]] = dict()
                        #if yes then update the corresponding value
                        scraped_data[LABEL_CATEGORY_MAPPING[key]].update(
                            {key: "".join(self.list_sanitizer(htmltree.xpath(value)))})
                    else:
                        #if the key is not in LABEL_CATEGORY_MAPPINGS then create a new key and add the value
                        scraped_data[key] = self.list_sanitizer(htmltree.xpath(value))

            #self.extract_media(response)
            #this gives us pdf_list, vid_list and img_list which is stored in scraped_data dictionary by creating new dictionary entries            
            scraped_data['images'], scraped_data['videos'], scraped_data['pdfs'] = self.extract_media(response)

            #now update the whole scraped data with self.post_processing method: basically convert it into a list
            scraped_data = self.post_processing(scraped_data)

            #if scraped_data is a list then extend scraped_data to it otherwise append it as a dictionary
            if isinstance(scraped_data, list):
                final_scrape.extend(scraped_data)
            else:
                final_scrape.append(scraped_data)

        #return the final_scrape data after it has been processed by self.format_final_result method
        return self.format_final_result(final_scrape)
            
    #write data to json
    def write_to_json(self,output):
        outf = open(self.json_output, 'w')
        outf.write(json.dumps(output))
        outf.close()

    #write data to csv
    def write_to_csv(self,output):
        flattened, headers = self.flatten_json(output) if isinstance(output, list) else self.flatten_json(list(output))
        headers = self.sort_csv_headers(headers)
        with open(self.csv_output, 'w', encoding="utf-8") as outf:
            dw = csv.DictWriter(outf, headers)
            dw.writeheader()
            dw.writerows(flattened)

    #sort csv
    def sort_csv_headers(self,headers):
        sorted_header_list = list()
        for sorted_head in EXCEL_SORT_LIST:
            for header in headers:
                if header.startswith(sorted_head):
                    headers.remove(header)
                    sorted_header_list.append(header)

        sorted_header_list.extend(headers)
        return sorted_header_list
    
    #flatten json
    def flatten_json(self,json_to_be_flattened):
        flattened_json = list()
        unique_headers = list()

        for prod in json_to_be_flattened:
            flattened = flatten(prod, '_')
            flattened_json.append(flattened)
            unique_headers = list(set().union(unique_headers, flattened.keys()))
        return flattened_json, unique_headers

#now test this module independently
if __name__ == "__main__":
    #******************************** test1 phase ******************************************************#
    #print("This is phase one test")
    #obj = scrapper("https://www.snapper.com","https://www.snapper.com/na/en_us/products.html",["//div[@class='heading parbase section']/h3/a/@href"],"//a[@class='carousel-products-item']/@href")

    #testing response
    #print(obj.get_request())
    #this will give us: <Response [200]>

    #catching the response and printing the response.content
    #resp = obj.get_request()
    #print(resp.content)
    #this will give us: the complete html page

    #now we will parse this response.content and see the result 
    #htmltree = obj.html_parser(resp.content)
    #print(htmltree)
    #this gave us: <Element html at 0x6770450>

    #now we will extract product links and category links from the html tree
    #category_links,product_links = obj.get_product_links(htmltree,obj.category_xpath_list,obj.product_xpath_string)
    #print("category:")
    #print(category_links)
    #this will gice us the values of hrefs that are in the heading parbase section div -> h3->a and make a list out of it
    #the list looks like this:
    #category:
    #['/na/en_us/products/push-mowers.html',
    #'/na/en_us/products/trimmers-blowers.html',
    #'/na/en_us/products/riding-mowers.html',
    #'/na/en_us/products/60v-max-products.html',
    #'/na/en_us/products/zero-turn-mowers.html',
    #'/na/en_us/products/snapper-xd-82v-max.html'
    #]
    #print("product links:")
    #print(product_links)
    #this gives us:
    #product links:
    #[]
    #so basicallythe productlist is empty because even on the url there is no carousel-products-item class anywhere

    #*************************** end of test1 phase ******************************************************#

    #********************************************* this is phase two ********************************************#
    print("This is phase 2 test")
    
    url = loader.params["url"]
    purl = loader.params["products_url"]
    links = loader.params["links"]
    product = loader.params["product"]
    product_info = loader.params["product_info"]
    allow_download = loader.params["allow_download"]
    json_output = loader.params['json_output']
    csv_output = loader.params['csv_output']
    
    spec_names = loader.spec_names
    
    obj2 = scrapper(url,purl,links,product,product_info,allow_download,spec_names,json_output,csv_output)
    obj2.greedy_scrape()

    #now get the product info out of the product_links list that was constructed
    info = obj2.get_product_info()

    #the result is stored in info and finally output is provided in json and csv format by these two functions 
    obj2.write_to_json(info)
    obj2.write_to_csv(info)
    #******************************************** end of phase two **********************************************#
    #print(info)
