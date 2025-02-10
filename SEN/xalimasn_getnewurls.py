#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Jan 12 2021

@author: diegoromero

This script updates xalimasn.com using sitemaps and queries per section. 
This script can be ran whenever needed (just make the necessary modifications).
 
"""
# Packages:
import random
import importlib
import sys
sys.path.append('../')
import os
import re
#from p_tqdm import p_umap
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
# %pip install dateparser
import dateparser
import pandas as pd

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## Custom Parser
def xalimasncom_story(soup):
    """
    Function to pull the information we want from xalimasn.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    # Get Title: 
    try:
        contains_title = soup.find("meta", {"property":"og:title"})
        article_title = contains_title['content']
        hold_dict['title']  = article_title   

    except:
        try:
            article_title = soup.find("title").text
            hold_dict['title']  = article_title 
        except: 
            article_title = None
            hold_dict['title'] = None
        
    # Get Main Text:
    try:
        maintext = ''
        for i in soup.find('div', {'class' : 'content-inner'}).find_all('p'):
            maintext += i.text
        hold_dict['maintext'] = maintext
       
    except: 
        contains_maintext = soup.find("meta", {"property":"og:description"})
        maintext = contains_maintext['content']
        hold_dict['maintext'] = maintext
    # Get Date
    try:
        contains_date = soup.find("meta", {"property":"article:published_time"})
        article_date = contains_date['content']
        #article_date = dateparser.parse(contains_date['content'])
        article_date = dateparser.parse(article_date, date_formats=['%d/%m/%Y'])
        hold_dict['date_publish'] = article_date  

    except:
        article_date = None
        hold_dict['date_publish'] = None  

    return hold_dict 


## COLLECTING URLS
urls = []

## NEED TO DEFINE SOURCE!
source = 'xalimasn.com'

# STEP 0: Get sitemap urls:
for i in range(191,194):
    url = "https://www.xalimasn.com/post-sitemap" + str(i) + ".xml"
    print("Extracting from: ", url)
    reqs = requests.get(url, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    for link in soup.findAll('loc'):
        urls.append(link.text)


    print("+ Number of urls so far: ", len(urls))


# STEP 2: Get rid or urls from blacklisted sources
blpatterns = ['/wp-json/', '/celebrites/', '/email/', '/videos/', ':80/', '/amp/', '/podcasts/', '/faits-divers/', '/photos/', '/religion/', '/radio', '/wp-content/', '/video-', '/revue-de-presse', 'revue-de-la-presse']

# List of unique urls:
dedup = urls.copy()
list_urls = []

for url in dedup:
    if "xalimasn.com" in url:
        count_patterns = 0
        for pattern in blpatterns:
            if pattern in url:
                count_patterns = count_patterns + 1
        if count_patterns == 0:
            list_urls.append(url)


print("Total number of USABLE urls found: ", len(list_urls))


## INSERTING IN THE DB:
url_count = 0
for url in list_urls[::-1]:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if "xalimasn.com" in url:
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
                    
                    ## Fixing Date, Main Text and Title:
                    response = requests.get(url, headers=header).text
                    soup = BeautifulSoup(response)

                    ## Title
                    article['title'] = xalimasncom_story(soup)['title'] 
                    ## Main Text
                    article['maintext'] = xalimasncom_story(soup)['maintext'] 
                    ## Date
                    article['date_publish'] = xalimasncom_story(soup)['date_publish'] 

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
                        print("Title: ", article['title'][0:25]," + Main Text: ", article['maintext'][0:30])
                        #print(article['maintext'])
                        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        #db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        print("DUPLICATE! Not inserted.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
            else:
                pass


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")