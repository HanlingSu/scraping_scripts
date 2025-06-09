#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 20, 2022

@author: diegoromero

This script updates '168.am' using sitemaps.

It can be run as often as one desires. 
"""
# Packages:
import random
import sys
sys.path.append('../')
import os
import re
#from p_tqdm import p_umap
#from tqdm import tqdm
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
#from dotenv import load_dotenv
from bs4 import BeautifulSoup
# %pip install dateparser
import dateparser
import pandas as pd
import cloudscraper
# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = '168.am'

### EXTRACTING ulrs from sitemaps:
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

list_urls = []

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)

hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

opinion_base = 'https://168.am/section/opinion/'
for p in range(1, 10):
    url = opinion_base + 'page/' +str(p)
    soup = BeautifulSoup(scraper.get(url).text)
    for i in soup.find_all('div', {'class' : 'realated-item clearfix'}):
        list_urls.append(i.find('a')['href'])
    print(len(list_urls))

## INSERTING IN THE DB:
url_count = 0
for url in list_urls:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if '168.am' in url:
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
                    article['source_domain'] = '168.am'
                    article['language'] = 'hy'
                    
                    ## Fixing what needs to be fixed:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Get Main Text:
                    if article['maintext'] == None:
                        try:
                            maintext =soup.find("div", {"class":"single-content-wrapper"}).text
                            article['maintext'] = maintext
                        except:
                            try:
                                contains_maintext = soup.find("meta", {"property":"og:description"})
                                maintext = contains_maintext['content']
                                article['maintext'] = maintext  
                            except: 
                                maintext = None
                                article['maintext']  = None

                    
                    ## Fixing Date:      168.am
                    indexam = url.index("168.am")
                    yearstr = url[indexam+7:indexam+11]
                    monthstr = url[indexam+12:indexam+14]
                    daystr = url[indexam+15:indexam+17]

                    article_date = datetime(int(yearstr),int(monthstr),int(daystr))
                    article['date_publish'] = article_date

                    ## Inserting into the db
                    try:
                        year = article['date_publish'].year
                        month = article['date_publish'].month
                        colname = f'opinion-articles-{year}-{month}'
                        article['primary_location'] = "ARM"
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
                        print(article['title'])
                        print(article['maintext'])
                        #print("+Title: ", article['title'][0:20]," +TEXT: ", article['maintext'][0:35])
                        print("Date extracted: ", article['date_publish'], " + Inserted! in ", colname, " - number of urls so far: ", url_count)
                        db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        print("DUPLICATE! Not inserted.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
            else:
                pass

print("Done inserting ", url_count, " of source ", source, " into the db.") 

