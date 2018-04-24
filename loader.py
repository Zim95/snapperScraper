#this is the loader file that loads config.json and params.yaml file
#and assigns it to values

import json
import yaml
from lxml import html

#loading up parameters from yaml file
with open('params.yaml', 'r') as f:
    #params is the yaml file
    #params contains all the parameters
    params = yaml.load(f)


#loading up configurations
with open('config.json', 'r') as f:
    #config is the json file
    #loaded up configurations to spec_names, specifications
    spec_names = json.load(f)

#this is a test module that will only run when this file is directly run from python
if __name__ == "__main__":
    #now lets print the whole value
    #print(params)
    #print(spec_names)

    #lets print params['links']
    #print(params['links'])
    #gives us: ["//div[@class='heading parbase section']/h3/a/@href"]

    #lets print params['products']
    #print(params['product'])
    #gives us: //a[@class='carousel-products-item']/@href

    #lets test params["product_info"]
    #print(params["product_info"])
    #gives us:{
        #'description': "//div[@class='product-detail-text']/p[2]/text()",
        #'specs': "//table[@class='table table-striped']/tbody/tr",
        #'features': "//div[@class='row']/div[@class='col-sm-6']/div[@class='two-wide-category-teaser']/*[preceding-sibling::div]/text()",
        #'categories': "//div[@class='breadcrumbs']/div[@class='container']/ol[@class='breadcrumb']"
    #}

    print(params["product_info"]["specs"])

