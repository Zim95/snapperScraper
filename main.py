########################################################################## import statements #######################################################################

#standard libraries
import requests
import time

#external self made files

#loader lodas the config.json and params.yaml file into spec_names and params
import loader
import mainClass
####################################################################### import statements end ######################################################################

######################################################################## MAIN CODE #################################################################################


#main function
def main():

    #get the starting time
    start = time.time()

    #the main code block

    #this is how we access the params and spec_names variable from loader.py
    #print(loader.params)
    #print(loader.spec_names)

    #so lets cache the required variables
    url = loader.params["url"]
    purl = loader.params["products_url"]
    links = loader.params["links"]
    product = loader.params["product"]
    product_info = loader.params["product_info"]
    allow_download = loader.params["allow_download"]
    json_output = loader.params['json_output']
    csv_output = loader.params['csv_output']
    
    spec_names = loader.spec_names
    
    obj = mainClass.scrapper(url,purl,links,product,product_info,allow_download,spec_names,json_output,csv_output)
    obj.greedy_scrape()

    #now get the product info out of the product_links list that was constructed
    info = obj.get_product_info()

    #the result is stored in info and finally output is provided in json and csv format by these two functions 
    obj.write_to_json(info)
    obj.write_to_csv(info)

    
    
    #stop time
    stop = time.time()

    #print the total time elapsed
    print("The total time elapsed is %s" % str(stop-start))
    
#the thing with if __name__ == "__main__" is to check if this code is imported or not
#if i print out __name__ in first.py then it will give me 'main'
#but if i import this code and run it on say another.py then i will get __name__ = first.py
#which tells us that this code was imported from first.py
#so now what we are doing is, we will run the main function only on this module.
#if this file is imported on another .py file then the value of __name__ will be main not __main__
#so the main() function won't be fired.

#so now we check if this file is being run directly by python or is this file being imported
if __name__ == "__main__":
    main()
##################################################################### MAIN CODE END ################################################################################
