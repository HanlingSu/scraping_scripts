#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Dec 23 2021

@author: diegoromero

This script updates kalerkantho.com using daily sitemaps.
It at least once every two months
 
"""
# Packages:
import random
import sys
sys.path.append('../')
import os
import re
from p_tqdm import p_umap
from tqdm import tqdm
from pymongo import MongoClient
import random
from urllib.parse import urlparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from pymongo.errors import CursorNotFound
import requests
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from dotenv import load_dotenv
from bs4 import BeautifulSoup
# %pip install dateparser
import dateparser
import pandas as pd

# db connection:
db = MongoClient('mongodb://ml4pAdmin:ml4peace@research-devlab-mongodb-01.oit.duke.edu').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


## COLLECTING URLS
urls = []
siteurls = []
usiteurls = []

## NEED TO DEFINE SOURCE!
source = 'kalerkantho.com'

# STEP 0: Get sitemap urls:
url = "https://www.kalerkantho.com/sitemap.xml"
print("Extracting from: ", url)
reqs = requests.get(url, headers=headers)
soup = BeautifulSoup(reqs.text, 'html.parser')
for link in soup.findAll('loc'):
    siteurls.append(link.text)
#for link in soup.find_all('a'):
#    urls.append(link.get('href')) 

for url in siteurls:
    if "sitemap-section.xml" in url:
        #if "/2021/12/24" in url:
        pass
    else:
        if "2022-05-" in url or '2022-06-' in url:
            usiteurls.append(url)
        else:
            pass

        
#dftest = pd.DataFrame(siteurls)  
#dftest.to_csv('/Users/diegoromero/Downloads/test.csv')  

print("Number of sitemaps found today: ", len(usiteurls))

# STEP 1: Get urls of articles from sitemaps:
for sitmp in usiteurls:
    print("Extracting from: ", sitmp)
    reqs = requests.get(sitmp, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    for link in soup.findAll('loc'):
        urls.append(link.text)
    #for link in soup.find_all('a'):
    #    urls.append(link.get('href')) 
    print("URLs so far: ", len(urls))

# Manually check urls:
#dftest = pd.DataFrame(list_urls)  
#dftest.to_csv('/Users/diegoromero/Downloads/test.csv')  

# STEP 2: Get rid or urls from blacklisted sources
blpatterns = ['/news_images/','/feature/','/miscellaneous/','/islamic-life/','/silalipi/','/sports/','/sub-editorial/','/tech-everyday/','/telecom/','/tuntuntintin/','/culture/']

clean_urls = []
for url in urls:
    if "kalerkantho.com" in url:
        count_patterns = 0
        for pattern in blpatterns:
            if pattern in url:
                count_patterns = count_patterns + 1
        if count_patterns == 0:
            clean_urls.append(url)

# List of unique urls:
list_urls = list(set(clean_urls))

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
            if "kalerkantho.com" in url:
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
                    
                    ## Fixing Date:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Get Title: 
                    try:
                        contains_title = soup.find("meta", {"property":"og:title"})
                        article_title = contains_title['content']
                        article['title']  = article_title   
                    except:
                        article_title = article['title']
                        article['title'] = article_title
        
                    # Get Main Text:
                    try:
                        # if /print-edition/ or /online/ (not /amp/) in url
                        maintext_contains = soup.findAll("p")
                        maintext = maintext_contains[4].text + " " + maintext_contains[5].text + " " + maintext_contains[6].text
                        article['maintext'] = maintext
                        # if /amp/ in url
                        #maintext_contains = soup.findAll("p")
                        #maintext = maintext_contains[1].text + " " + maintext_contains[2].text
                        #hold_dict['maintext'] = maintext
                    except: 
                        maintext = article['maintext']
                        article['maintext'] = maintext

                    # Get Date
                    try:
                        # if /print-edition/ or /online/ (not /amp/) in url
                        contains_date = soup.find("meta", {"itemprop":"datePublished"})
                        contains_date = contains_date['content']
                        #article_date = dateparser.parse(contains_date,date_formats=['%d/%m/%Y'])
                        article_date = dateparser.parse(contains_date)
                        article['date_publish'] = article_date 

                        # if /amp/ in url
                        #contains_date = soup.find("meta", {"property":"article:published_time"})
                        #contains_date = contains_date['content']
                        ##article_date = dateparser.parse(contains_date,date_formats=['%d/%m/%Y'])
                        #article_date = dateparser.parse(contains_date)
                        #hold_dict['date_publish'] = article_date  
                    except:
                        article_date = article['date_publish'] 
                        article['date_publish'] = article_date 

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
                        #print(article['date_publish'])
                        #print(article['title'][0:20])
                        #print(article['maintext'][0:50])
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