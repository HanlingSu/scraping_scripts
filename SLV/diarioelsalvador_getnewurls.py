#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 20, 2022

@author: diegoromero

This script updates 'diarioelsalvador.com' using sitemaps.

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

# db connection:
uri = 'mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true'
db = MongoClient(uri).ml4p

source = 'diarioelsalvador.com'

### EXTRACTING ulrs from sitemaps:
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## CHANGE: initial and final sitemaps

# Site Maps:
#https://diarioelsalvador.com/post-sitemap5.xml
#

initialsitemap = 1
finalsitemap = 8


# Scraping from sitemaps
# for j in range(initialsitemap,finalsitemap+1):
#     # to keep urls:
#     urls = []

#     # URL of the sitemap to scrape:
#     url = 'https://diarioelsalvador.com/post-sitemap' + str(j) + '.xml'

#     print("First Sitemap: ", url)

#     reqs = requests.get(url, headers=headers)
#     soup = BeautifulSoup(reqs.text, 'html.parser')

#     for link in soup.findAll('loc'):
#         urls.append(link.text)
#     #for link in soup.find_all('a'):
#     #    urls.append(link.get('href')) 

#     print("Obtained ", len(urls), " URLs from sitemap number ",str(j))

#     # KEEP ONLY unique URLS:
#     dedupurls = list(set(urls))

#     # STEP 1: Get rid or urls from blacklisted sources
#     blpatterns = ['/dedeportes/']

#     list_urls = []
#     for url in dedupurls:
#         if url == "":
#             pass
#         else:
#             if url == None:
#                 pass
#             else:
#                 try: 
#                     count_patterns = 0
#                     for pattern in blpatterns:
#                         if pattern in url:
#                             count_patterns = count_patterns + 1
#                     if count_patterns == 0:
#                         list_urls.append(url)
#                         #print(url)
#                 except:
#                     pass


list_urls = pd.read_csv('/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/SLV/diarioelsalvador.csv')['0']
print(len(list_urls))
print("Obtained ", len(list_urls), " USABLE URLs from sitemap number ",str(j))


## INSERTING IN THE DB:
url_count = 0
for url in list_urls:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if 'diarioelsalvador.com' in url:
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
                    article['source_domain'] = 'diarioelsalvador.com'
                    article['language'] = 'es'
                    
                    ## Fixing what needs to be fixed:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    
                    ## Fixing Date:
                    if article['date_publish'] == None:
                        try:
                            contains_date = soup.find("meta", {"property":"article:published_time"})
                            contains_date = contains_date['content']
                            article_date = dateparser.parse(contains_date,date_formats=['%d/%m/%Y'])
                            article['date_publish'] = article_date  
                        except:
                            article['date_publish'] = None

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
                        url_count = url_count + 1
                        #print(article['date_publish'])
                        #print(article['date_publish'].month)
                        print(article['title'][0:25])
                        print(article['maintext'][0:50])
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

print("Done inserting ", url_count, " manually collected urls from sitemap number ", str(j), " of source ", source, " into the db.") 
