#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Feb 3 2021

@author: diegoromero

This script updates 'cnnespanol.cnn.com' using sitemaps.

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
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
#db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
#db = MongoClient('mongodb://ml4pAdmin:ml4peace@research-devlab-mongodb-01.oit.duke.edu').ml4p

source = 'cnnespanol.cnn.com'

### EXTRACTING ulrs from sitemaps:
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

urls = []

# Test:
#url = 'https://cnnespanol.cnn.com/post-sitemap1.xml'

#reqs = requests.get(url, headers=headers)
#soup = BeautifulSoup(reqs.text, 'html.parser')

#for link in soup.findAll('loc'):
#    urls.append(link.text)

#print(len(urls))
#dftest = pd.DataFrame(urls)  
#dftest.to_csv('/Users/diegoromero/Dropbox/cnn_Test.csv')  

# date_dict = {} 
# # post-sitemap 
for j in range(129,134):
    url = 'https://cnnespanol.cnn.com/post-sitemap' + str(j) + '.xml'

    print("First Sitemap: ", url)

    reqs = requests.get(url, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    for url_elem, date_elem in zip(soup.find_all('loc'), soup.find_all('lastmod')):
        link = url_elem.text.strip()
        urls.append(link)
    
    print(len(urls))

# # video-sitemap 
# for j in range(149,151):
#     url = 'https://cnnespanol.cnn.com/video-sitemap' + str(j) + '.xml'

#     print("First Sitemap: ", url)

#     reqs = requests.get(url, headers=headers)
#     soup = BeautifulSoup(reqs.text, 'html.parser')

    
#     for url_elem, date_elem in zip(soup.find_all('loc'), soup.find_all('lastmod')):
#         link = url_elem.text.strip()
#         urls.append(link)

#         last_mod = date_elem.text.strip()
#         last_mod2 = dateparser.parse(last_mod, date_formats=['%d/%m/%Y'])

#         date_dict[link] = last_mod2


#     print(len(urls))

# # KEEP ONLY unique URLS:
# dedupurls = list(set(urls))
dedupurls = pd.read_csv('Downloads/peace-machine/peacemachine/getnewurls/INT/cnnespanol.csv')['url']

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
            except:
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
            if 'cnnespanol.cnn.com' in url:
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
                    article['source_domain'] = 'cnnespanol.cnn.com'
                    
                    ## Fixing what needs to be fixed:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    ## Inserting into the db
                    try:
                        year = date_dict[url].year
                        month = date_dict[url].month
                        colname = f'articles-{year}-{month}'
                        print(date_dict[url])
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
                        #print("TEXT: ", article['maintext'])
                        print("Date extracted: ", date_dict[url], " + Inserted! in ", colname, " - number of urls so far: ", url_count)
                        db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        print("DUPLICATE! Not inserted.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
            else:
                pass
print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
