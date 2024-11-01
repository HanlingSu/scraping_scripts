#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Oct 14, 2021

This script obtains full urls from Wayback, scrapes them using newsplease, 
and inserts them into the db. 

You need to specify: start date, end date and sources

@author: diegoromero
"""
import bs4
from bs4 import BeautifulSoup
from newspaper import Article
import random
import sys
import os
import re

import requests as rq
import urllib.request
from bs4 import BeautifulSoup as bs
from time import sleep
from time import time
from random import randint
from warnings import warn
import json
import pandas as pd
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



## DEFINE PERIOD (FORMAT: YYYYMMDD)
# from date:
fromdate = "20230201" 
# to date:
todate = "202300501"

## DEFINE SOURCE(S):
# sources = ['euronews.com','neweasterneurope.eu','eurasianet.org','centralasianews.net']
sources = ['eldiario.ec']

# DEFINE DABASE:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p


## Process to extract urls from Wayback and then scrape them using Newsplease:
for source in sources:
    # Querying the web archive database for the specified sources in the specified period:
    url = "https://web.archive.org/cdx/search/cdx?url=" + source + "&matchType=domain&collapse=urlkey&from=" + fromdate + "&to=" + todate + "&output=json"

    urls = rq.get(url).text
    parse_url = json.loads(urls) #parses the JSON from urls.
    parse_url = list(parse_url)
    
    print("Working on ", len(parse_url), "urls from Wayback Machine's archive for", source)
    
    ## Extracts timestamp and original columns from urls and compiles a url list.
    url_list = []
    url_count = 0
    processed_url_count = 0
    for i in range(1,len(parse_url)):
        if str(parse_url[i][4]) == "200":
            orig_url = parse_url[i][2]
            if orig_url == "https://www." + source + "/":
                pass
            else:
                if orig_url == "https://" + source + "/":
                    pass
                else:
                    tstamp = parse_url[i][1]
                    waylink = tstamp+'/'+orig_url
                    ## Compiles final url pattern:
                    final_url = 'https://web.archive.org/web/' + waylink
                    url_list.append(final_url)
                    print(final_url)
                    ## SCRAPING WAYBACK URLS USING NEWSPLEASE:
                    try:
                        #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
                        header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                        response = requests.get(final_url, headers=header)
                        # process
                        article = NewsPlease.from_html(response.text, url=final_url).__dict__
                        # add on some extras
                        article['date_download']=datetime.now()
                        article['download_via'] = "wayback_alt"
                        article['source_domain'] = source
                        
                        soup = BeautifulSoup(response.content, 'html.parser')
            
                        try:
                            soup.find_all('li', {'itemprop' : 'itemListElement'})
                            for i in soup.find_all('li', {'itemprop' : 'itemListElement'}):
                                if i.find('meta', {'content' : '2'}):
                                    category = i.find('span', {'itemprop' : 'name'}).text.strip()
                                else:
                                    pass
                            print(category)
                        except:
                            category = 'News'
                        # try: 
                        #     category = soup.find('meta', {'name':"cXenseParse:edi-categories"})['content']
                        # except:
                        #     category = 'news'


                        if category in ['Deportes', 'Opinión', 'Farándula', 'Cultura']:
                            article['title']  = 'From uninterested category!'
                            article['date_publish'] = None
                            print(article['title'], category)
                            pass
                        else:

                            if article['date_publish']:
                                print('Scraped date:', article['date_publish'])
                            if article['title']:
                                print('Scraped title:', article['title'])
                            if article['maintext']:
                                print('Scraped maintext:', article['maintext'][:50])

                        # insert into the db
                        try:
                            year = article['date_publish'].year
                            month = article['date_publish'].month
                            colname = f'articles-{year}-{month}'
                            #print(article)
                        except:
                            colname = 'articles-nodate'
                        if year >= 2012 or  colname == 'articles-nodate':
                            try:
                                #TEMP: deleting the stuff i included with the wrong domain:
                                #myquery = { "url": final_url, "source_domain" : 'web.archive.org'}
                                #db[colname].delete_one(myquery)
                                # Inserting article into the db:
                                db[colname].insert_one(article)
                                print("Inserted! in ", colname)
                                if colname != 'articles-nodate':
                                    url_count += 1
                                    print('Inserted ', url_count, 'URLs...')
                                #db['urls'].insert_one({'url': article['url']})
                            except DuplicateKeyError:
                                print("DUPLICATE! Not inserted.")
                            
                    except Exception as err: 
                        print("ERRORRRR......", err)
                        pass
                    processed_url_count += 1
                    print('\n',processed_url_count, '/', len(parse_url), 'articles have been processed ...\n')
   

    print("Done with ", len(url_list), "urls from ",  source)

print("Done with ALL sources.")


    # WRITING DATASET:
    #dftest = pd.DataFrame(url_list)  
    #dftest.to_csv('/Users/diegoromero/Dropbox/WAYBACK_Test0.csv')  
    #print("Done with ", source)