#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Nov 11 2021

@author: diegoromero

This script updates balkaninsight.com using daily sitemaps AND keyword searches,
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
import cloudscraper
import math

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# cloudscraper (to bypass cloudflare)
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)
# headers for scraping
#headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
#headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
headers = {'User-Agent': 'Mozilla/5.0'} #header settings

## COLLECTING URLS
urls = []

## NEED TO DEFINE SOURCE!
source = 'balkaninsight.com'


## Step 0: define starting month and year:
year_up = 2023
month_up = 6

## STEP 1: COLLECTING URLS FROM KEYWORD SEARCHES:
# keywords:
keywords = ['all-balkans-premium','all-the-news-from-albania','all-the-news-from-bosnia-and-herzegovina','all-the-news-from-bulgaria','all-the-news-from-croatia','all-the-news-from-montenegro','all-the-news-from-kosovo','all-the-news-from-north-macedonia','all-the-news-from-montenegro','all-the-news-from-romania','all-the-news-from-serbia','all-the-news-from-montenegro','balkan-transitional-justice-home/balkan-transitional-justice-news','reporting-democracy/insight','far-right-news','balkan-media-watch-news','russia-in-the-balkans-news','turkey-and-the-balkans-news','refugee-crisis-news','china-in-the-balkans-news','focus-on-covid-19-outbreak-news','digital-rights-news','bulgaria-north-macedonia-dispute-news','foreign-fighters-in-ukraine','all-the-news-from-the-balkans']
nombpages = ['40','6','4','6','4','8','8','4','6','4','8','8','12','12','4','4','4','2','2','2','2','4','4','4','40']

#https://balkaninsight.com/balkan-transitional-justice-home/balkan-transitional-justice-news/
#https://balkaninsight.com/balkan-transitional-justice-home/balkan-transitional-justice-news/?pg=4
#https://balkaninsight.com/all-the-news-from-croatia/
#https://balkaninsight.com/all-the-news-from-albania/?pg=3

for word in keywords:
    indexword = keywords.index(word)
    endnumberx = nombpages[indexword]
    for i in range(1, int(endnumberx)+1):
        if i == 1:
            initial_url = "https://balkaninsight.com/" + word + "/"
        else:
            initial_url = "https://balkaninsight.com/" + word + "/?pg=" + str(i)
        # URLs from page":
        
        # withouth cloudscraper:
        #req = requests.get(initial_url, headers = headers)
        #soup = BeautifulSoup(req.content, 'html.parser')
        #soup = BeautifulSoup(req.text, 'html.parser')

        # with cloudscraper:
        soup = BeautifulSoup(scraper.get(initial_url).text)

        #for link in soup.findAll('loc'):
        #    urls.append(link.text)
        for link in soup.find_all('a'):
            urls.append(link.get('href')) 
        print("URLs so far: ", len(urls))
    
    print(word, " ", len(urls))

# Manually check urls:
#list_urls = list(set(urls))
#dftest = pd.DataFrame(list_urls)  
#dftest.to_csv('/Users/diegoromero/Downloads/test_CSM.csv')  

# STEP 2: Get rid or urls from blacklisted sources
blpatterns = ['/wp-json/', '/Images/', '/tag/', '/category/', '/author/']
clean_urls = []
for url in urls:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            print(url)
            if "https://" in url:
                count_patterns = 0
                for pattern in blpatterns:
                    if pattern in url:
                        count_patterns = count_patterns + 1
                if count_patterns == 0:
                    clean_urls.append(url)
            else:
                count_patterns = 0
                for pattern in blpatterns:
                    if pattern in url:
                        count_patterns = count_patterns + 1
                if count_patterns == 0:
                    new_url = "https://balkaninsight.com/" + url
                    clean_urls.append(new_url)

# List of unique urls:
list_urls = list(set(clean_urls))

# Manually check urls:
#dftest = pd.DataFrame(list_urls)  
#dftest.to_csv('/Users/diegoromero/Downloads/test_csm.csv')  

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
            if "balkaninsight.com" in url:
                print(url, "FINE")
                ## SCRAPING USING NEWSPLEASE:
                try:
                    #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
                    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                    response = requests.get(url, headers=header)
                    # process
                    soup = BeautifulSoup(scraper.get(url).text)
                    article = NewsPlease.from_html(scraper.get(url).text, url=url).__dict__
                    #article = NewsPlease.from_html(response.text, url=url).__dict__
                    # add on some extras
                    article['date_download']=datetime.now()
                    article['download_via'] = "Direct2"
                    
                    ## Fixing Date:
                    #soup = BeautifulSoup(response.content, 'html.parser')

                    #try:
                    #    contains_date = soup.find("div", {"class":"post-meta-date"}).text
                        #contains_date = soup.find("i", {"class":"fa fa-calendar"}).text
                    #    article_date = dateparser.parse(contains_date, date_formats=['%d/%m/%Y'])
                    #    article['date_publish'] = article_date
                    #except:
                    #    article_date = article['date_publish']
                    #    article['date_publish'] = article_date

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
                        #db[colname].insert_one(article)
                        # OLD:
                        #if article['date_publish'].month >= month_up:
                        #    if article['date_publish'].year >= year_up:
                        #        url_count = url_count + 1
                                # Inserting article into the db:
                        #        db[colname].insert_one(article)
                        #        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        #        db['urls'].insert_one({'url': article['url']})
                        #    else: 
                        #        print("Not from ", year_up)
                        #else:
                        #    print("Not within the month range.")
                        # NEW:
                        if article['date_publish'].year == year_up:
                            if article['date_publish'].month >= month_up:
                                url_count = url_count + 1
                                # Inserting article into the db:
                                db[colname].insert_one(article)
                                print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                                db['urls'].insert_one({'url': article['url']})
                            else:
                                print("Wrong month")
                        else:
                            if article['date_publish'].year > year_up:
                                url_count = url_count + 1
                                # Inserting article into the db:
                                db[colname].insert_one(article)
                                print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                                db['urls'].insert_one({'url': article['url']})
                            else: 
                                print("From before ", year_up) 
                    except DuplicateKeyError:
                        print("DUPLICATE! Not inserted.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
            else:
                pass


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")