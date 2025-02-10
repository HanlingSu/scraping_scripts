#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Jul 27, 2022

@author: Hanling

This script updates prothomalo.com using daily sitemaps.
It can be run whenever necessary.
 
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
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## NEED TO DEFINE SOURCE!
source = 'prothomalo.com'

base = "https://prothomalo.com/sitemap/sitemap-daily-"

direct_URLs = []
for year in range(2024, 2025):
    for month in range(8, 9):
        for day in range(1, 32):
            year_str = str(year)
            
            if month >= 10:
                month_str = str(month)
            else:
                month_str = '0' + str(month)

            if day >= 10:
                day_str = str(day)
            else:
                day_str = '0' + str(day)
            
            url = base + year_str + '-' + month_str +'-' + day_str+'.xml'
            print("Extracting from ", url)

            reqs = requests.get(url, headers=headers)
            soup = BeautifulSoup(reqs.content, 'html.parser')
            for link in soup.findAll('loc'):
                direct_URLs.append(link.text)
            print("Urls so far: ",len(direct_URLs))


blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

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
        article['source_domain'] = source
        article['language'] = 'bn'
        print('newsplease date', article['date_publish'])

        ## Fixing what needs to be fixed:
        soup = BeautifulSoup(response.content, 'html.parser')

        try:
            #article_title = soup.find("title").text
            contains_title = soup.find("meta", {"property":"og:title"})
            article_title = contains_title['content']
            article['title']  = article_title   
        except:
            try:
                article_title = soup.find("h1", {'class' : 'storytitleInfo-m__story-headline__30dXX'}).text
                article['title']  = article_title   
            except:
                article_title = article['title']
                article['title'] = article_title
        print('newsplease title', article['title'])

        ## FIX main text:
        try:
            soup.find_all('div', {'class' : 'story-element story-element-text'})
            maintext = ''
            for i in  soup.find_all('div', {'class' : 'story-element story-element-text'}):
                for j in i.find_all('p'):
                    maintext += j.text
            article['maintext'] = maintext
        except: 
            try:
                soup.find_all('p')
                maintext = ''
                for i in  soup.find_all('p'):
                    maintext += i.text
                article['maintext'] = maintext
            except: 
                maintext = article['maintext']
                article['maintext'] = maintext
        print('newsplease maintext', article['maintext'][:50])


            
        try:
            year = article['date_publish'].year
            month = article['date_publish'].month
            colname = f'articles-{year}-{month}'
            #print(article)
        except:
            colname = 'articles-nodate'
        #print("Collection: ", colname)
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
            print("DUPLICATE! Not inserted.")
    except Exception as err: 
        print("ERRORRRR......", err)
        pass
    processed_url_count += 1
    print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')



print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
