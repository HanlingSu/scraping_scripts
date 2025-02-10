#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import random
import sys
sys.path.append('../')
import os
import re
from p_tqdm import p_umap
from tqdm import tqdm
from pymongo import MongoClient
from urllib.parse import urlparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from pymongo.errors import CursorNotFound
import requests
from newsplease import NewsPlease
from bs4 import BeautifulSoup
import dateparser
import pandas as pd

# db connection:
uri = 'mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true'
db = MongoClient(uri).ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## NEED TO DEFINE SOURCE!
source = 'timesofindia.indiatimes.com'

## Custom Parser
def timesofindia_story(soup):
    """
    Function to pull the information we want from indiatimes.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    
    # Get Title
    try:
        article_title = soup.find("title").text
        hold_dict['title'] = article_title   
    except:
        hold_dict['title'] = None
    
    # Get Main Text
    try: 
        maintext_contains = soup.find("meta", {"property":"og:description"})
        maintext = maintext_contains['content']
        hold_dict['maintext'] = maintext
    except: 
        hold_dict['maintext'] = None

    # Get Date
    try: 
        date_contains = soup.find("meta", {"itemprop":"datePublished"})
        date = date_contains['content']
        hold_dict['date_publish'] = datetime.strptime(date, '%Y-%m-%d')  # Ensure correct date format
    except:
        try:
            # Handle alternative date format or location
            date_contains = soup.find("div", {"class":"yYIu- byline"}).text
            date_contains = date_contains.lower().replace(",", "")
            vcontent = date_contains.split()
            months = ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]
            monthfoundn, indexmonth, dayn, yearn = None, None, None, None
            for i, val in enumerate(vcontent):
                if any(month in val for month in months):
                    indexmonth = i
                    monthfoundn = months.index(val[:3]) + 1  # Shorten month to 3 characters
            dayn = vcontent[indexmonth]
            yearn = vcontent[indexmonth + 1]
            hold_dict['date_publish'] = datetime(int(yearn), monthfoundn, int(dayn))
        except:
            hold_dict['date_publish'] = None

    return hold_dict

# STEP 0: Get sitemap urls for INSERT month:
siteurls = []

url = "https://timesofindia.indiatimes.com/staticsitemap/toi/sitemap-index.xml"
print("Extracting from: ", url)
reqs = requests.get(url, headers=headers)
soup = BeautifulSoup(reqs.text, 'html.parser')
for link in soup.findAll('loc'):
    foundurl = link.text
    # Only consider sitemaps 
    if "/2024" in foundurl and "-December" in foundurl:
        print(foundurl)
        siteurls.append(link.text)

print("Number of sitemaps found for December 2024: ", len(siteurls))

# STEP 1: Get urls of articles from sitemaps:
for sitmp in siteurls:
    urls = []
    print("Extracting from: ", sitmp)
    reqs = requests.get(sitmp, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    for link in soup.findAll('loc'):
        urls.append(link.text)

    print("URLs so far: ", len(urls))

    # STEP 2: Get rid of URLs from blacklisted sources
    blpatterns = ['/entertainment/', '/sports/', '/life-style/', '/gadgets-news/', '/most-searched-products/']
    clean_urls = []
    for url in urls:
        if "timesofindia.indiatimes.com" in url:
            count_patterns = 0
            for pattern in blpatterns:
                if pattern in url:
                    count_patterns += 1
            if count_patterns == 0:
                clean_urls.append(url)

    # List of unique urls:
    list_urls = list(set(clean_urls))

    print("Total number of usable urls found: ", len(list_urls))
    time.sleep(30)

    ## INSERTING IN THE DB:
    url_count = 0
    for url in list_urls:
        if url == "" or url is None:
            continue
        if "timesofindia.indiatimes.com" in url:
            ## SCRAPING USING NEWSPLEASE:
            try:
                url_count += 1
                header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                response = requests.get(url, headers=header)
                
                # Scrape article using NewsPlease and BeautifulSoup
                article = NewsPlease.from_html(response.text, url=url).__dict__
                
                # Parse article content using custom parser
                soup = BeautifulSoup(response.content, 'html.parser')
                article['title'] = timesofindia_story(soup)['title']
                article['maintext'] = timesofindia_story(soup)['maintext']
                article['date_publish'] = timesofindia_story(soup)['date_publish']
                
                # Filter articles by date - only keep August 2024 articles
                if article['date_publish'] and article['date_publish'].year == 2024 and article['date_publish'].month == 12:
                    # Add additional metadata to the article
                    article['date_download'] = datetime.now()
                    article['download_via'] = "Direct2"
                    article['source_domain'] = "timesofindia.indiatimes.com"

                    # Insert article into MongoDB
                    try:
                        colname = f'articles-2024-12'
                        db[colname].insert_one(article)
                        print("+ URL: ", url)
                        print("+ DATE: ", article['date_publish'])
                        print("+ TITLE: ", article['title'][0:200])
                        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                    except DuplicateKeyError:
                        print("DUPLICATE! Not inserted.")
                else:
                    print(f"Skipping article {url} - Not from Dec 2024 or no valid date.")
            
            except Exception as err:
                print("ERRORRRR......", err)

    print("Done inserting ", url_count, " manually collected URLs from ", source, " into the DB. Now waiting 63 seconds...")
    time.sleep(63)
