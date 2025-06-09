#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Jul 27 2022

@author: Hanling

This script updates dailyjanakantha.com using daily archives.
It at least once every two months
 
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
import json


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## NEED TO DEFINE SOURCE!
source = 'dailyjanakantha.com'

base = "https://www.dailyjanakantha.com/news/"

direct_URLs = []
# 706475
for i in range(752713, 789177):
    direct_URLs.append(base + str(i))

blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

final_result = direct_URLs.copy()
## INSERTING IN THE DB:
url_count = 0
processed_url_count = 0

for url in final_result:
    try:
        #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
        header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        response = requests.get(url, headers=header)
        # process
        article = NewsPlease.from_html(response.text, url=url).__dict__
        # add on some extras
        article['date_download']=datetime.now()
        article['download_via'] = "Direct2"
        article['language'] = "bn"
        
        ## Fixing Date:
        soup = BeautifulSoup(response.text, 'html.parser')
        article['url'] = soup.find('meta', property = 'og:url')['content']
        print(article['url'])
        # Get Title: 
        try:
            title = soup.find("meta", {"property":"og:title"})['content']
            article['title']  = title   
        except:
            article_title = soup.find('h1').text
            article['title'] = article_title

        if article['title']:
            print('newsplease title', article['title'])

        # Get Main Text:
        try:
            if soup.find("div", {'id' : 'contentDetails'}).find_all('p'):
                maintext = ''
                for i in soup.find("div", {'id' : 'contentDetails'}).find_all('p'):
                    maintext += i.text
                article['maintext'] = maintext.strip()
            if not article['maintext']:
                maintext = soup.find('h1').text
                article['maintext'] = maintext
        except: 
            article['maintext'] = None
                # print(maintext)
        if article['maintext']:
            print('newsplease maintext', article['maintext'][:50])

        # Get Date
        try:
            date = json.loads(soup.find('script',{'type':"application/ld+json"}).contents[0])['datePublished']
            article['date_publish'] = dateparser.parse(date)
        except:
            article['date_publish'] =  article['date_publish']  
        print('newsplease date', article['date_publish'])


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
                print("Inserted! in ", colname, " - number of urls so far: ", url_count)
            else:
                print("Inserted! in ", colname)
            db['urls'].insert_one({'url': article['url']})

        except DuplicateKeyError:
            # myquery = { "url": url}
            # db[colname].delete_one(myquery)
            # Inserting article into the db:
            # db[colname].insert_one(article)
            # print("DUPLICATE! UPDATED.")
            print("DUPLICATE! Not inserted.")
    except Exception as err: 

        print("ERRORRRR......", err)
        pass
    processed_url_count += 1
    print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db." )