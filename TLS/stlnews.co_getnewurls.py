#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sep 27, 2023

@author: Hanling

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

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p


### EXTRACTING ulrs from sitemaps:
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}



source = 'stltimorleste.com'
direct_URLs = []
sitemap_base = 'https://stltimorleste.com/sitemap_index'

#35
for i in range(1, 2): # smaller numbered-sitemaps host the more recent stuff.
    sitemap = sitemap_base + str(i) + '.xml'
    print('Scraping from ', sitemap, ' ...')
    hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    req = requests.get(sitemap, headers = hdr)
    soup = BeautifulSoup(req.content)
    item = soup.find_all('loc')

    for i in item:
        direct_URLs.append(i.text)

    print('Now scraped ', len(direct_URLs), ' articles from previous sitemaps.')

# blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
# blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
# direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

final_result = direct_URLs.copy()

## INSERTING IN THE DB:
url_count = 0
processed_url_count = 0
for url in final_result:
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

        #blacklist by category:
        try:
            category = soup.find('meta', {'itemprop' : 'articleSection'})['content']
        except:
            category = 'News'
        
        if category in ['Культура', 'Наука', 'Спорт', 'Досуг']:
                        # culture,  science, sport, leisure
            article['date_publish'] = None
            article['maintext'] = None
            article['title'] = 'From uninterested category!'
            print(article['title'], category)
        else: 
            ## Fixing Date: 
            contains_date = soup.find("meta",{"itemprop":"datePublished"})['content']
            article_date = dateparser.parse(contains_date)
            article['date_publish'] = article_date
            print('Newsplease Date: ', article['date_publish'])

            # Get Main Text:
            if not article['maintext']:
                try:
                    maintext = ''
                    for i in soup.find('div', {'class' : 'td_block_wrap tdb_single_content tdi_103 td-pb-border-top td_block_template_9 td-post-content tagdiv-type'}).find('div', {'class' : 'tdb-block-inner td-fix-index'}).find_all('p'):
                        maintext += i.text
                    if maintext !='':
                        article['maintext'] = maintext.strip()
                except:
                    try:
                        article['maintext']  =soup.find('div', {'class' : 'td_block_wrap tdb_single_content tdi_103 td-pb-border-top td_block_template_9 td-post-content tagdiv-type'}).find('div', {'class' : 'tdb-block-inner td-fix-index'}).text
                    except: 
                        maintext = None
                        article['maintext']  = None

            print('Newsplease Maintext: ', article['maintext'][:50])

            # code = detectlanguage.detect(article['maintext'])[0]['language']
            code =  detect(article['maintext'])
        
            article['language'] = code
            
            
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
    print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')


print("Done inserting ", url_count, " manually collected urls from year ", str(year), " of source ", source, " into the db.") 


