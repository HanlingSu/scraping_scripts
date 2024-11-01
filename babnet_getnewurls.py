#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Dec 27 2021

@author: diegoromero

This script updates babnet.net using section query.
It can be run whenever necessary.
 
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


def babnetnet_story(soup):
    """
    Function to pull the information we want from babnet.net stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}

    # Get Title: 
    try:
        contains_title = soup.find("meta", {"property":"og:title"})
        article_title = contains_title['content']
        hold_dict['title']  = article_title   
    except:
        article_title = None
        hold_dict['title']  = None
        
    # Get Main Text:
    try:
        contains_maintext = soup.find("meta", {"property":"og:description"})
        maintext = contains_maintext['content']
        hold_dict['maintext'] = maintext  
    except: 
        maintext = None
        hold_dict['maintext']  = None

    # Get Date
    try:
        contains_date = soup.find("meta", {"itemprop":"datePublished"})
        contains_date = contains_date['content']
        #article_date = dateparser.parse(contains_date,date_formats=['%d/%m/%Y'])
        article_date = dateparser.parse(contains_date)
        hold_dict['date_publish'] = article_date 
    except:
        hold_dict['date_publish'] = None
   
    return hold_dict 

# db connection:
db = MongoClient('mongodb://ml4pAdmin:ml4peace@research-devlab-mongodb-01.oit.duke.edu').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## NEED TO DEFINE SOURCE!
source = 'babnet.net'

## STEP 0: OBTAINING URLS:
urls = []

# STEP 0: Get articles from sections:
# sections:
sections = ['politique','national-news','regions','sante','monde','justice']
# CHANGE endnumbers for each section in accordance with how far 
# back you need to go:
endnumber = ['80','60','40','40','40','40'] 

for section in sections:
    indexword = sections.index(section)
    endnumberx = endnumber[indexword]
    #https://www.babnet.net/politique.php
    #https://www.babnet.net/politique.php?p=59401 (by 30*x + 1)

    for i in range(0, int(endnumberx)+2):
        if i == 0:
            url = "https://www.babnet.net/" + section + ".php"
            print("Section: ", section, " -> URL: ", url)

            reqs = requests.get(url, headers=headers)
            soup = BeautifulSoup(reqs.text, 'html.parser')

            for link in soup.find_all('a'):
                urls.append(link.get('href')) 
            print("URLs so far: ", len(urls))
        else:
            pnumber = (i*30)+1
            url = "https://www.babnet.net/" + section + ".php?p=" + str(pnumber)
            
            print("Section: ", section, " -> URL: ", url)

            reqs = requests.get(url, headers=headers)
            soup = BeautifulSoup(reqs.text, 'html.parser')

            for link in soup.find_all('a'):
                urls.append(link.get('href')) 
            print("URLs so far: ", len(urls))

### PREPARING THE DAY'S URLS:
# List of unique urls:
list_urls = []
dedup = list(set(urls))

for url in dedup:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if ".php" in url:
                pass
            else:
                if "/images/" in url:
                    pass
                else: 
                    if "https://" in url:
                        pass
                    else:
                        newurl = "https://www.babnet.net/" + url
                        list_urls.append(newurl)

print("Number of usable urls: ", len(list_urls))

#df = pd.DataFrame(list_urls)
#df.to_csv('/Users/diegoromero/Downloads/jomhouria_check.csv')

## INSERTING IN THE DB:
url_count = 0
for url in list_urls:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if "babnet.net" in url:
                #print(url, "FINE")
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
                    
                    # FIXING: DATE, TITLE, MAIN TEXT
                    hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                    req = requests.get(url, headers = hdr)
                    soup = BeautifulSoup(req.text, 'html.parser')

                    article['title'] = babnetnet_story(soup)['title']
                    article['maintext'] = babnetnet_story(soup)['maintext']
                    article['date_publish'] = babnetnet_story(soup)['date_publish']

                    # Choosing the correct db collection:
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
                        print("URL: ",url)
                        print("+ DATE:: ", article['date_publish'])
                        print("+ TITLE: ", article['title'][0:20])
                        print("+ MAIN TEXT: ", article['maintext'][0:40])
                        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        print("DUPLICATE! Not inserted.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
            else:
                pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")