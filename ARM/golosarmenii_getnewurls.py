#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 20, 2022

@author: diegoromero, Hanling

This script updates 'golosarmenii.am' using sitemaps. -> This source is protected by cloudflare

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
import detectlanguage
from langdetect import detect
detectlanguage.configuration.api_key = "81762acd6a7244ef736911adbadb09e3"


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'golosarmenii.am'

### EXTRACTING ulrs from sitemaps:
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
#headers = {'User-Agent': 'MLP Bot'}

## CHANGE: initial and final sitemaps
yearini = 2024
yearend = 2024


# Scraping from sitemaps
for j in range(yearini,yearend+1):
    # to keep urls:
    urls = []

    # URL of the sitemap to scrape:
    url = 'https://golosarmenii.am/sitemap/default/index/?year=' + str(j)

    print("First Sitemap: ", url)

    reqs = requests.get(url, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    for link in soup.findAll('loc'):
        urls.append(link.text)
    #for link in soup.find_all('a'):
    #    urls.append(link.get('href')) 


    
    print("Obtained ", len(urls), " URLs from year ", str(j))

    # KEEP ONLY unique URLS:
    dedupurls = urls.copy()

    # STEP 1: Get rid or urls from blacklisted sources
    blpatterns = ['/gallery/', '/tag/', '/author/', '/category/', '/tv_show/']

    list_urls = []
    for url in dedupurls:
        if url == "":
            pass
        else:
            if url == None:
                pass
            else:
                try: 
                    count_patterns = 0
                    for pattern in blpatterns:
                        if pattern in url:
                            count_patterns = count_patterns + 1
                    if count_patterns == 0:
                        list_urls.append(url)
                        #print(url)
                except:
                    pass

    print("Obtained ", len(list_urls), " USABLE URLs from year ",str(j))


    ## INSERTING IN THE DB:
    url_count = 0
    processed_url_count = 0
    for url in list_urls[::-1]:
        if url == "":
            pass
        else:
            if url == None:
                pass
            else:
                if 'golosarmenii.am' in url:
                    print(url, "FINE")
                    ## SCRAPING USING NEWSPLEASE:
                    try:
                        #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
                        #header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                        header = {'User-Agent': 'MLP Bot'}
                        response = requests.get(url, headers=header)
                        # process
                        article = NewsPlease.from_html(response.text, url=url).__dict__
                        # add on some extras
                        article['date_download']=datetime.now()
                        article['download_via'] = "Direct2"
                        article['source_domain'] = 'golosarmenii.am'

                        print('Newsplease Title: ', article['title'])

                        ## Fixing what needs to be fixed:
                        soup = BeautifulSoup(response.content, 'html.parser')
                                        
                        ## Fixing Date: 
                        contains_date = soup.find("meta",{"itemprop":"datePublished"})['content']
                        article_date = dateparser.parse(contains_date)
                        article['date_publish'] = article_date
                        print('Newsplease Date: ', article['date_publish'])
        
                        # Get Main Text:
                        if not article['maintext']:
                            try:
                                maintext = ''
                                for i in soup.find_all("p",{"itemprop":"articleBody"}):
                                    maintext += i.text
                                article['maintext'] = maintext.strip()
                            except:
                                try:
                                    contains_maintext = soup.find("meta", {"property":"og:description"})
                                    maintext = contains_maintext['content']
                                    article['maintext'] = maintext  
                                except: 
                                    maintext = None
                                    article['maintext']  = None

                        print('Newsplease Maintext: ', article['maintext'][:50])
                        # code = detectlanguage.detect(article['maintext'])[0]['language']
                        code =  detect(article['maintext'])
                        if code == 'ru':
                            article['language'] = code
                        elif code =='et':
                            article['language'] = 'hy'
                        else:
                            article['language'] = article['language'] 
                        
                        print('This article is wrote in', article['language'] )

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
                            #print(article['title'])
                            #print(article['maintext'])
                            #print("+Title: ", article['title'][0:20]," +TEXT: ", article['maintext'][0:35])
                            print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                            db['urls'].insert_one({'url': article['url']})
                        except DuplicateKeyError:
                            print("DUPLICATE! Not inserted.")
                    except Exception as err: 
                        print("ERRORRRR......", err)
                        pass
                    processed_url_count += 1
                    print('\n',processed_url_count, '/', len(list_urls), 'articles have been processed ...\n')

                else:
                    pass

    print("Done inserting ", url_count, " manually collected urls from year ", str(j), " of source ", source, " into the db.") 

