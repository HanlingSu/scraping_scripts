#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Jan 12 2021

@author: diegoromero

This script updates lequotidien.sn using queries per section. 
This script can be ran whenever needed (just make the necessary modifications).
 
"""
# Packages:
import random
import importlib
import sys
sys.path.append('../')
import os
import re
#from p_tqdm import p_umap
from tqdm import tqdm
from pymongo import MongoClient
import random
from urllib.parse import urlparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from pymongo.errors import CursorNotFound
import requests
from newsplease import NewsPlease
from dotenv import load_dotenv
from bs4 import BeautifulSoup
# %pip install dateparser
import dateparser
import pandas as pd

# db connection:
#db = MongoClient('mongodb://ml4pAdmin:ml4peace@research-devlab-mongodb-01.oit.duke.edu').ml4p
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


## COLLECTING URLS
urls = []

## NEED TO DEFINE SOURCE!
source = 'lequotidien.sn'

# STEP 1: Extracting urls from key sections:
sections = ['politique','societe','economie','actualites']
number = ['8','8','8','8']

#sections = ['politique','societe','economie','actualites']
#number = ['186','36','123','680']

for sect in sections:
    indexsect = sections.index(sect)
    numberx = number[indexsect]
    for i in range(1,int(numberx)+1):
        if i == 1:
            url = "https://lequotidien.sn/category/" + sect + "/"
        else:
            url = "https://lequotidien.sn/category/" + sect + "/page/" + str(i) + "/"

        print("Extracting from ", url)

        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        for link in soup.find_all('a'):
            urls.append(link.get('href')) 

        print("+ Number of urls so far: ", len(urls))


# Manually check urls:
#dftest = pd.DataFrame(list_urls)  
#dftest.to_csv('/Users/diegoromero/Downloads/test.csv')  

# STEP 2: Get rid or urls from blacklisted sources
blpatterns = ['/wp-json/', '/photo/', ':80/', '/index.php/', '/wp-content/', '/images/','/category/']

# List of unique urls:
dedup = list(set(urls))
list_urls = []

for url in dedup:
    if "lequotidien.sn" in url:
        count_patterns = 0
        for pattern in blpatterns:
            if pattern in url:
                count_patterns = count_patterns + 1
        if count_patterns == 0:
            list_urls.append(url)


print("Total number of USABLE urls found: ", len(list_urls))


## INSERTING IN THE DB:
url_count = 0
for url in list_urls:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if "lequotidien.sn" in url:
                print(url, "FINE")
                ## SCRAPING USING NEWSPLEASE:
                try:
                    #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
                    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                    response = requests.get(url, headers=header)
                    # process
                    article = NewsPlease.from_html(response.text, url=url).__dict__
                    # add on some extras
                    article['date_download']=datetime.now()
                    article['download_via'] = "Direct2"
                    
                    ## Fixing Date, Main Text and Title:
                    response = requests.get(url, headers=header).text
                    soup = BeautifulSoup(response)

                    ## Title
                    #article['title'] = ferloocom_story(soup)['title'] 
                    ## Main Text
                    #article['maintext'] = ferloocom_story(soup)['maintext'] 
                    ## Date
                    #article['date_publish'] = ferloocom_story(soup)['date_publish'] 

                    ## Inserting into the db
                    try:
                        year = article['date_publish'].year
                        month = article['date_publish'].month
                        colname = f'articles-{year}-{month}'
                        #print(article)
                    except:
                        colname = 'articles-nodate'
                    try:
                        #TEMP: deleting the stuff i included with the wrong domain:
                        #myquery = { "url": final_url, "source_domain" : 'web.archive.org'}
                        #db[colname].delete_one(myquery)
                        # Inserting article into the db:
                        db[colname].insert_one(article)
                        # count:
                        url_count = url_count + 1
                        print(article['date_publish'])
                        print("Title: ", article['title'][0:25]," + Main Text: ", article['maintext'][0:30])
                        #print(article['maintext'])
                        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        print("DUPLICATE! Not inserted.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
            else:
                pass


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")