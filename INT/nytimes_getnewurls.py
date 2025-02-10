#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Edited on Jan 19 2024

@author: Hanling

This script updates nytimes.com using daily sitemaps.
It can be run as often as one desires. 
 
"""
# Packages:
import random
import sys
import cloudscraper
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
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
#db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
#db = MongoClient('mongodb://ml4pAdmin:ml4peace@research-devlab-mongodb-01.oit.duke.edu').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)

## COLLECTING URLS
urls = []

## NEED TO DEFINE SOURCE!
source = 'nytimes.com'
#https://www.nytimes.com/issue/todayspaper/2021/09/01/todays-new-york-times
#https://www.nytimes.com/sitemap/2021/11/05/
## STEP 0: Define dates

for year in range(2024, 2025):
    year_str = str(year)
    for month in range(12, 13):
        if month < 10:
            month_str = '0' + str(month)
        else:
            month_str = str(month)
        for day in range(5, 10):
            if day < 10:
                day_str = '0' + str(day)
            else:
                day_str = str(day)

            url = "https://www.nytimes.com/sitemaps/new/sitemap-" + year_str + "-" + month_str + ".xml.gz" 
            print("Extracting from: ", url)
            reqs = requests.get(url, headers=headers)
            soup = BeautifulSoup(reqs.text, 'html.parser')
            try:
                for i in soup.find_all('loc'):
                    urls.append(i.text)
            except:
                pass
            print("URLs so far: ", len(urls))


# STEP 1: Get rid or urls from blacklisted sources
blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
urls = [word for word in urls if not blacklist.search(word)]


# List of unique urls:
list_urls = urls.copy()


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
            if "nytimes.com" in url:
                print(url, "FINE")
                ## SCRAPING USING NEWSPLEASE:
                try:

                    soup = BeautifulSoup(scraper.get(url).text)
                    article = NewsPlease.from_html(scraper.get(url).text).__dict__
                    article['date_download']=datetime.now()
                    article['download_via'] = "Direct2"

                    print("newsplease date: ", article['date_publish'])
                    print("newsplease title: ", article['title'])
                    print("newsplease maintext: ", article['maintext'][:50])

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
                        if colname != 'articles-nodate':
                            url_count = url_count + 1
                        #print(article['date_publish'])
                        #print(article['date_publish'].month)
                        #print(article['title'][0:100])
                        #print(article['maintext'][0:100])
                        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        #db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        print("DUPLICATE! Not inserted.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
            else:
                pass


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")