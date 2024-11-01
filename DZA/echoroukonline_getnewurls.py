#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 2023

@author: diegoromero

This script updates echoroukonline.com using sitemaps.

"""

# Packages:
import time
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

# Adding Browser / User-Agent Filtering should help ie.
# will give you only desktop firefox User-Agents on Windows
scraper = cloudscraper.create_scraper(browser={'browser': 'firefox','platform': 'windows','mobile': False})

# db connection:
uri = 'mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true'
db = MongoClient(uri).ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## NEED TO DEFINE SOURCE!
source = 'echoroukonline.com'

# Custom Parser
def echoroukonlinecom_story(soup):
    """
    Function to pull the information we want from echoroukonline.com stories
    """
    hold_dict = {}

    # Get Title: 
    try:
        article_titlec = soup.find("meta", {"property":"og:title"})
        article_title = article_titlec["content"]
        hold_dict['title']  = article_title   
    except:
        try:
            article_title = soup.find("title").text
            hold_dict['title']  = article_title 
        except:
            hold_dict['title']  = None
        
    # Get Main Text:
    try:
        listoftexts = soup.findAll("p")
        text = listoftexts[0].text + listoftexts[1].text
        text = text.strip()
        hold_dict['maintext'] = text
    except:
        hold_dict['maintext'] = None  

    # Get Date
    try:
      # <meta property="article:published_time" content="2023-04-25T11:35:24+00:00" />
        containsdate = soup.find("meta", {"property":"article:published_time"})
        article_date = containsdate['content']
        hold_dict['date_publish'] = dateparser.parse(article_date)
    except Exception as err:
        hold_dict['date_publish'] = None
        #print("Error when trying to get the date", err)

    return hold_dict
##

##
sitemap1n = 419
sitemap2n = 421

#https://www.echoroukonline.com/sitemap_index.xml
#https://www.echoroukonline.com/post-sitemap412.xml
for i in range(sitemap1n, sitemap2n+1):
    ## STEP 1: COLLECTING URLS
    urls = []
    if i == 1:
        url = "https://www.echoroukonline.com/post-sitemap.xml"
    else:
        url = "https://www.echoroukonline.com/post-sitemap" + str(i) + ".xml"

    print("Extracting from ", url)
    time.sleep(3)

    #reqs = requests.get(url, headers=headers)
    # Protected by cloudflare, use this instead:
    html = scraper.get(url).content
    soup = BeautifulSoup(html, 'html.parser')

    for link in soup.find_all('loc'):
        urlx = link.text
        urls.append(urlx) 
        print(urlx)

    print("+ Number of urls so far: ", len(urls))

    # STEP 2: Get rid or urls from blacklisted sources + DUPLICATES
    list_urls = list(set(urls))

    print("Total number of USABLE urls found: ", len(list_urls))
    time.sleep(2)

    ## INSERTING IN THE DB:
    url_count = 0
    for url in list_urls:
        if url == "":
            pass
        else:
            if url == None:
                pass
            else:
                if "echoroukonline.com" in url:
                    ## SCRAPING USING NEWSPLEASE:
                    try:
                        # count:
                        url_count = url_count + 1
                        #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
                        #header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                        #response = requests.get(url, headers=header)
                        # Protected by cloudflare, use this instead:
                        html = scraper.get(url).content
                        soup = BeautifulSoup(html, 'html.parser')
                        article = NewsPlease.from_html(html, url=url).__dict__
                        # add on some extras
                        article['date_download']=datetime.now()
                        article['download_via'] = "Direct2"
                        article['source_domain'] = source
                        article['language'] = 'ar'
                        
                        ## Fixing main texts when needed:                        
                        # Title:
                        print('+ titlebefore: ',article['title'])
                        article['title'] = echoroukonlinecom_story(soup)['title']

                        # Main Text
                        article['maintext'] = echoroukonlinecom_story(soup)['maintext']

                        # Date of Publication
                        article['date_publish'] = echoroukonlinecom_story(soup)['date_publish']

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
                            print("+ URL: ",url)
                            print("+ DATE: ",article['date_publish'], " - Month: ",article['date_publish'].month)
                            print("+ TITLE: ",article['title'][0:200])
                            print("+ MAIN TEXT: ",article['maintext'][0:200])
                            print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                            pogressm = url_count/len(list_urls)
                            print(" --> Progress:", str(pogressm))
                        except DuplicateKeyError:
                            pogressm = url_count/len(list_urls)
                            print("DUPLICATE! Not inserted. --> Progress:", str(pogressm))
                    except Exception as err: 
                        print("ERRORRRR......", err)
                        #pass
                else:
                    pass

    print("Done inserting ", url_count, " manually collected urls from ",  source)
    time.sleep(2)