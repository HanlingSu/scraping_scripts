#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Nov 11 2021

@author: diegoromero

This script updates lemonde.fr using weekly sitemaps (using the date of every Monday).
It can be run as often as one desires.
"""
# Packages:
import random
import sys
sys.path.append('../')
import os
import re
import time
from p_tqdm import p_umap
from tqdm import tqdm
from pymongo import MongoClient
from urllib.parse import urlparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError, CursorNotFound
import requests
from newsplease import NewsPlease
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import dateparser
import pandas as pd

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}

# COLLECTING URLS
urls = []

## NEED TO DEFINE SOURCE!
source = 'lemonde.fr'
yearn = "2024"
mondays = ["09-02", "09-09", "09-16", "09-23", "09-30"]  # Enter the dates of every Monday you want to visit

for monday in mondays:
    url = f"https://www.lemonde.fr/sitemap/articles/{yearn}-{monday}.xml"
    print("Extracting from: ", url)
    reqs = requests.get(url, headers=headers)
    if reqs.status_code == 200:
        soup = BeautifulSoup(reqs.text, 'html.parser')
        for link in soup.findAll('loc'):
            urls.append(link.text)
        print("URLs so far: ", len(urls))
    else:
        print(f"Failed to retrieve {url}, status code: {reqs.status_code}")

# Filter URLs based on blacklisted patterns
blpatterns = ['/livres/', '/idees/', '/video/', '/sport/', '/football/', '/cinema/', '/blog/', '/culture/', '/m-le-mag/', '/podcasts/', '/sciences/', '/smart-cities/', '/televisions-radio/']
clean_urls = [url for url in urls if all(pattern not in url for pattern in blpatterns)]

print("Total number of USABLE urls found: ", len(clean_urls))

# INSERTING IN THE DB:
url_count = 0
processed_url_count = 0

# Filter out specific ranges or set as needed
list_urls = clean_urls[42 + 52 + 52 + 51 + 42:-130]

for url in reversed(list_urls):
    if url and "lemonde.fr" in url:
        print(url, "FINE")
        # SCRAPING USING NEWSPLEASE:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                article = NewsPlease.from_html(response.text, url=url).__dict__

                if not article.get('title') or not article.get('maintext'):
                    print(f"Skipping article due to missing content: {url}")
                    continue

                # Add some additional data
                article['date_download'] = datetime.now()
                article['download_via'] = "Direct2"

                print("newsplease date: ", article['date_publish'])
                print("newsplease title: ", article['title'])
                print("newsplease maintext: ", article['maintext'][:50])

                # Inserting into the DB
                try:
                    year = article['date_publish'].year
                    month = article['date_publish'].month
                    colname = f'articles-{year}-{month}'
                except:
                    colname = 'articles-nodate'

                try:
                    db[colname].insert_one(article)
                    if colname != 'articles-nodate':
                        url_count += 1
                    print(f"Inserted! in {colname} - number of urls so far: {url_count}")
                    db['urls'].insert_one({'url': article['url']})
                except DuplicateKeyError:
                    print("DUPLICATE! Not inserted.")
            else:
                print(f"Failed to retrieve article, status code: {response.status_code}")
        except Exception as err:
            print("ERRORRRR......", err)
            pass

        processed_url_count += 1
        print(f'\n{processed_url_count} / {len(list_urls)} articles have been processed ...\n')
        if processed_url_count % 50 == 0:
            time.sleep(1200)
    else:
        pass

print(f"Done inserting {url_count} manually collected urls from {source} into the db.")
