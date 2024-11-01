#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Jul 27 2022

@author: Hanling

This script updates bd-pratidin.com using sitemaps (only 1 month's worth of daily articles) 
and scraping urls from sections.

It can be run as often as one desires. 
 
"""
# Packages:
import random
import sys
from xxlimited import Xxo
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


# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


## COLLECTING URLS
direct_URLs = []

## NEED TO DEFINE SOURCE!
source = 'bd-pratidin.com'

base = 'https://www.bd-pratidin.com/en/opinion/'
for p in range(0, 98, 14):
    url = base+str(p)

    reqs = requests.get(url, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    for link in soup.findAll('a', {'class':'list-item'}):
            direct_URLs.append(link['href'])
    print("Urls so far: ",len(direct_URLs))


# List of unique urls:
direct_URLs = ['https://www.bd-pratidin.com/en/' + i for i in direct_URLs]
final_result = list(set(direct_URLs))


print("Total number of USABLE urls found: ", len(final_result))


## INSERTING IN THE DB:
url_count = 0
processed_url_count = 0

for url in final_result:
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
        article['source_domain'] = "bd-pratidin.com"
        article['language'] = 'bn'
        print('newsplease date', article['date_publish'])

        ## Fixing what needs to be fixed:
        soup = BeautifulSoup(response.content, 'html.parser')

        # TITLE:
        #if article['title'] == None:
        try:
            contains_title = soup.find("meta", {"property":"og:title"})
            article_title = contains_title['content']
            article['title'] = article_title
        except:
            article_title = article['title']
            article['title'] = article_title
        print('newsplease title', article['title'])
        # MAIN TEXT:
        #if article['maintext'] == None:
        try:
            maintext_contains = soup.findAll("p")
            maintext = maintext_contains[0].text + " " + maintext_contains[1].text + " " + maintext_contains[2].text
            article['maintext'] = maintext
        except:
            article_text = article['maintext']
            article['maintext'] = article_text
        print('newsplease maintext', article['maintext'][:50])


        ## Inserting into the db
        try:
            year = article['date_publish'].year
            month = article['date_publish'].month
            colname = f'opinion-articles-{year}-{month}'
            article['primary_location'] = "BGD"
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
                print("Inserted! in ", colname, " - number of urls so far: ", url_count)
            else:
                print("Inserted! in ", colname)
            db['urls'].insert_one({'url': article['url']})
            
        except DuplicateKeyError:
            #myquery = { "url": url}
            #db[colname].delete_one(myquery)
            # Inserting article into the db:
            #db[colname].insert_one(article)
            # count:
            #url_count = url_count + 1
            #print(" + Rescraping DUPLICATE -- Date extracted: ", article['date_publish'], " + Inserted! in ", colname, " - number of urls so far: ", url_count)
            #db['urls'].insert_one({'url': article['url']})
            print("DUPLICATE! Not inserted.")
    except Exception as err: 
        print("ERRORRRR......", err)
        pass
    processed_url_count += 1
    print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
