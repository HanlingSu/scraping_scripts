# Packages:
import sys
import os
import re
import getpass
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np 
from tqdm import tqdm
from pymongo import MongoClient
import bs4
from bs4 import BeautifulSoup
from newspaper import Article
from dateparser.search import search_dates
import dateparser
import requests
from urllib.parse import quote_plus
import urllib.request
import time
from time import time
import random
from random import randint, randrange
from warnings import warn
import json
from pymongo import MongoClient
from urllib.parse import urlparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from pymongo.errors import CursorNotFound
from newsplease import NewsPlease
from dotenv import load_dotenv

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

source = 'elwatan-dz.com'

direct_URLs = []

\
# for i in range(128, 128 +1):
#     sitemap = 'https://tiempo.hn/post-sitemap' + str(i) + '.xml' 
    
#     reqs = requests.get(sitemap, headers=headers)
#     soup = BeautifulSoup(reqs.text, 'html.parser')

#     for link in soup.find_all('loc'):
#         direct_URLs.append(link.text)

#     print(len(direct_URLs))

category = ['actualite', 'economie', 'international', 'regions',\
    'lepoque', 'contributions']

page_start = [1, 1, 1, 1, 1, 1]
page_end = [40, 22, 13, 2, 20, 3]
# page_end = [312, 169, 221, 19, 159, 25]
for c, ps, pe in zip(category, page_start, page_end):
    for p in range(ps, pe+1):
        url = 'https://elwatan-dz.com/categories/' + c + '?page=' + str(p)
        print(url)
        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')
        for link in soup.find_all('h3', {'class' :'text-xl line-clamp-2 mt-2 sm:mt-0'}):
            direct_URLs.append(link.find('a')['href'])
        print('Now collected', len(direct_URLs), 'articles ...')

# blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
# blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
# direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

final_result = direct_URLs.copy()
url_count = 0
processed_url_count = 0
for url in final_result:
    if url:
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
            article['language'] = 'fr'
            try:
                date = soup.find('div', {'class' : 'flex items-center text-sm'}).find('span').text[:10]
                article['date_publish'] = dateparser.parse(date,  settings = {'DATE_ORDER' : 'DMY'})
            except:
                article['date_publish'] = dateparser.parse(soup.find('div', {'class' : 'flex items-center text-sm'}).find('span').text[:10])
            print("newsplease date: ", article['date_publish'])
            print("newsplease title: ", article['title'])

            if not article['maintext']:
                try:
                    maintext = soup.find('div', {'id' : 'article-content'}).text
                    article['maintext'] = maintext
                except:
                    maintext = ''
                    for i in soup.find('div', {'id' : 'article-content'}).find_all('p'):
                        maintext += i.text
                    article['maintext'] = maintext

            if "Par" in article['maintext'][:5]:
                article['maintext'] = ' '.join(article['maintext'].split('\n')[1:])
            
            if article['maintext']:
                print("newsplease maintext: ", article['maintext'][:50])                    
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
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
                url_count = url_count + 1
                print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                db['urls'].insert_one({'url': article['url']})
            except DuplicateKeyError:
                print("DUPLICATE! Not inserted.")
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
