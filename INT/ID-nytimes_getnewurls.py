#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Edited on Jan 19 2024

@author: Hanling

This script updates nytimes.com using daily sitemaps.
It can be run as often as one desires. 
"""
# Packages:
import random
import sys
import cloudscraper
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
from newsplease import NewsPlease
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import dateparser
import pandas as pd

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)

## COLLECTING URLS
urls = []

## NEED TO DEFINE SOURCE!
source = 'nytimes.com'

## STEP 0: Define dates 
year = 2024
month = 9
year_str = str(year)
month_str = '0' + str(month)  

# Loop through each day in August
for day in range(1, 32):  
    if day < 10:
        day_str = '0' + str(day)
    else:
        day_str = str(day)

    url = f"https://www.nytimes.com/sitemaps/new/sitemap-{year_str}-{month_str}.xml.gz"
    print("Extracting from:", url)
    reqs = requests.get(url, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    try:
        for i in soup.find_all('loc'):
            urls.append(i.text)
    except:
        pass
    print("URLs so far:", len(urls))

# STEP 1: Get rid of urls from blacklisted sources
blacklist = [(i['blacklist_url_patterns']) for i in db.sources.find({'source_domain': source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
urls = [word for word in urls if not blacklist.search(word)]

# List of unique urls:
list_urls = urls.copy()

print("Total number of USABLE urls found:", len(list_urls))

## INSERTING IN THE DB:
url_count = 0
for url in list_urls:
    if url == "" or url is None:
        continue
    if "nytimes.com" in url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            soup = BeautifulSoup(scraper.get(url).text, 'html.parser')
            article = NewsPlease.from_html(scraper.get(url).text).__dict__
            article['date_download'] = datetime.now()
            article['download_via'] = "Direct2"

            # Filter to only insert articles 
            if article['date_publish'] and article['date_publish'].year == 2024 and article['date_publish'].month == 9:
                print("newsplease date:", article['date_publish'])
                print("newsplease title:", article['title'])
                print("newsplease maintext:", article['maintext'][:50])

                ## Inserting into the db
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
                    print("Inserted! in", colname, "- number of urls so far:", url_count)
                except DuplicateKeyError:
                    print("DUPLICATE! Not inserted.")
            else:
                print("Article not from september 2024, skipping.")
        except Exception as err: 
            print("ERRORRRR......", err)
            pass

print("Done inserting", url_count, "manually collected urls from", source, "into the db.")
