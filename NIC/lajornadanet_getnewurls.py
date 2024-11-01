#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Nov 20 2022

@author: Hanling

This script updates 'laprensani.com' using daily sitemaps.
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
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from dotenv import load_dotenv
from bs4 import BeautifulSoup
# %pip install dateparser
import dateparser
import pandas as pd

import time

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


source = 'lajornadanet.com'

category = ['noticias/regional','noticias/mundo','noticias/mexico', 'tag/ucrania', 'tag/estados-unidos', 'tag/canada', ]

page_start = [1, 1, 1, 1, 1, 1]
page_end = [2, 4, 4, 2, 2, 2]
direct_URLs = []
file_address = "/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/NIC/lajornadanet9.csv"

for c, ps, pe in zip(category, page_start, page_end):
    for p in range(ps, pe):
        url = 'https://lajornadanet.com/' + c + '/page/' +str(p)
        print(url)
        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')
        for i in soup.find_all('h2', {'class' : 'entry-title'}):
            direct_URLs.append(i.find('a')['href'])
        print('Now collected', len(direct_URLs), 'articles...')
        time.sleep(10)
blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

final_result = list(set(direct_URLs))


print('The total count of final result is: ', len(final_result))
failed_urls = []
url_count = 0
processed_url_count = 0
for url in final_result:
    if url:
        print(url, "FINE")
        time.sleep(5)
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
            if 'Por ' in article['maintext'][:5]:
                article['maintext'] = '\n'.join(article['maintext'].split('\n')[1:])
            if not article['maintext']:
                try:
                    maintext = soup.find('div', {'class' : 'penci-entry-content entry-content'}).text
                    article['maintext'] = maintext
                except:
                    article['maintext'] = article['title']
            print('newsplease maintext', article['maintext'][:50])
            print('newsplease title', article['title'])
            print('newsplease date', article['date_publish'])

            ## Fixing what needs to be fixed:
            soup = BeautifulSoup(response.content, 'html.parser')

            ## Inserting into the db
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                if '/opinion-2/' in url or '/opinion/' in url:
                    colname = f'opinion-articles-{year}-{month}'
                else:
                    colname = f'articles-{year}-{month}'
                #print(article)
            except:
                colname = 'articles-nodate'
            try:
                #TEMP: deleting the stuff i included with the wrong domain:
                #myquery = { "url": final_url, "source_domain" : 'web.archive.org'}
                #db[colname].delete_one(myquery)
            
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
            failed_urls.append(url)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

pd.DataFrame(failed_urls).to_csv(file_address)

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
