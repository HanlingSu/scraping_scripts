#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Feb 3 2021
Modified on Nov 11 2024 
@author : Iman
@author: diegoromero

This script updates asiatimes.com using sitemaps.

It can be run as often as one desires. 
"""
# Packages:
import random
import sys
from xml.dom import xmlbuilder
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
#from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from dotenv import load_dotenv
from bs4 import BeautifulSoup
# %pip install dateparser
import dateparser
import pandas as pd
import time

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
#db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
#db = MongoClient('mongodb://ml4pAdmin:ml4peace@research-devlab-mongodb-01.oit.duke.edu').ml4p

source = 'asiatimes.com'

### EXTRACTING ulrs from sitemaps:
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

urls = []

# Define Pages you'll scrape from the sitemap
page_0 = 36
page_1 = 38
pageslist = list(range(page_0, page_1))

# Define the dates you want to scrape
yearmonth = "2024/12"

#https://asiatimes.com/post-sitemap65.xml
#"https://asiatimes.com/post-sitemap" + str(pagex) + ".xml"

# Sitemaps:
for pagex in pageslist:
    url = "https://asiatimes.com/post-sitemap" + str(pagex) + ".xml"
    print("Obtaining URLs from this sitemap: ", url)

    reqs = requests.get(url, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    # print(soup)
    for link in soup.findAll('loc'):
        urls.append(link.text)

    print("+ URLs so far: ", len(urls))


# KEEP ONLY unique URLS:
dedupurls = list(set(urls))

# STEP 1: Get rid or urls from blacklisted sources
blpatterns = ['/opinion/']

list_urls = []
for url in dedupurls:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if yearmonth in url:
                try: 
                    count_patterns = 0
                    for pattern in blpatterns:
                        if pattern in url:
                            count_patterns = count_patterns + 1
                    if count_patterns == 0:
                        list_urls.append(url)
                except:
                    pass
            else:
                pass

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
            if 'asiatimes.com' in url:
                print(url, "FINE")
                time.sleep(10)
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
                    article['source_domain'] = 'asiatimes.com'
                    
                    ## Fixing what needs to be fixed:
                    #soup = BeautifulSoup(response.content, 'html.parser')

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
                        #print(article['date_publish'].month)
                        #print(article['title'])
                        print("+TITLE: ", article['title'][0:20], " +MAIN TEXT: ", article['maintext'][0:25])
                        print("Date extracted: ", article['date_publish'], " + Inserted! in ", colname, " - number of urls so far: ", url_count)
                        #db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        myquery = { "url": url, "source_domain" : 'asiatimes.com'}
                        db[colname].delete_one(myquery)
                        
                        db[colname].insert_one(article)
                        print("DUPLICATE --> +TITLE: ", article['title'][0:20], " +MAIN TEXT: ", article['maintext'][0:25])
                        print("Date extracted: ", article['date_publish'], " + Inserted! in ", colname, " - number of urls so far: ", url_count)
                        # db['urls'].insert_one({'url': article['url']})
                        # print("DUPLICATE! Not inserted.")

                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
            else:
                pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")