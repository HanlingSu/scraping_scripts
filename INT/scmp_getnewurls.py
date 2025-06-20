#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Nov 11 2021

@author: diegoromero

This script updates scmp.com using daily sitemaps.
It can be run as often as one desires. 
 
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
#from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from dotenv import load_dotenv
from bs4 import BeautifulSoup
# %pip install dateparser
import dateparser
import pandas as pd

# db connection:
#db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


## COLLECTING URLS
urls = []

## NEED TO DEFINE SOURCE!
source = 'scmp.com'

## NEED TO DEFINE STARTING MONTH TO UPDATE: 
yearup = 2025
monthstart = 2  


# STEP O: get urls from sitemaps:,'https://www.scmp.com/sitemap_article.xml','https://www.scmp.com/sitemap_economy.xml','https://www.scmp.com/sitemap_business.xml'
sitemaps = ['https://www.scmp.com/sitemap/articles.xml']

for url in sitemaps:
    print("Extracting from: ", url)
    reqs = requests.get(url, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    for link in soup.findAll('loc'):
        urls.append(link.text)
    #for link in soup.find_all('a'):
    #    urls.append(link.get('href')) 
    print("URLs so far: ", len(urls))

# Manually check urls:
#list_urls = list(set(urls))
#dftest = pd.DataFrame(list_urls)  
#dftest.to_csv('/Users/diegoromero/Downloads/test.csv')  


# STEP 1: Get rid or urls from blacklisted sources
blpatterns = ['/sport/', '/culture/', '/lifestyle/', '/magazines/', '/comment/']

clean_urls = []
for url in urls:
    if "scmp.com" in url:
        count_patterns = 0
        for pattern in blpatterns:
            if pattern in url:
                count_patterns = count_patterns + 1
        if count_patterns == 0:
            clean_urls.append(url)

# List of unique urls:
list_urls = clean_urls.copy()

# Manually check urls:
#dftest = pd.DataFrame(list_urls)  
#dftest.to_csv('/Users/diegoromero/Downloads/test.csv')  
print("Total number of USABLE urls found: ", len(list_urls))


## INSERTING IN THE DB:
url_count = 0
for url in list_urls[5000:5500]:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if "scmp.com" in url:
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
                    #soup = BeautifulSoup(response.content, 'html.parser')
                    #try:
                    #    contains_date = soup.find("meta", {"property":"article:published_time"}).text
                    #    contains_date = contains_date['content']
                    #    article_date = dateparser.parse(contains_date, date_formats=['%d/%m/%Y'])
                    #    print("Checked date: ", article_date )
                        #article['date_publish'] = article_date
                    #except:
                    #    print("NO NEED")
                        #article_date = article['date_publish']
                        #article['date_publish'] = article_date

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
                        if colname != 'articles-nodate':
                            if article['date_publish'].year == yearup:
                                if int(article['date_publish'].month)== monthstart:
                                    # Inserting article into the db:
                                    db[colname].insert_one(article)
                                    # count:
                                    url_count = url_count + 1
                                    print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                                    db['urls'].insert_one({'url': article['url']})
                                else:
                                    print("No need to insert. Wrong Month.")
                            else:
                                print("No need to insert. Wrong Year.")
                        else:
                            print("No Date.")                               
                        print(article['date_publish'])
                        #print(article['date_publish'].month)
                        #print(article['title'][0:100])
                        #print(article['maintext'][0:100])
                    except DuplicateKeyError:
                        print("DUPLICATE! Not inserted.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
            else:
                pass


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")