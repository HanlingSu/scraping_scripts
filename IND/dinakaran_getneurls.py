#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 3 2023

@author: Rethis + Diego

This script updates dinakaran.com 
 
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

import math

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## NEED TO DEFINE SOURCE!
source = 'dinakaran.com'

#################
# Custom Parser #
def dinakarancom_story(soup):
    """
    Function to pull the information we want from dinakaran.com stories
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
#################


# Obtaing urls from sitemap
#https://www.dinakaran.com/sitemap_index.xml
for j in range(223,336):
    # STEP 1: OBTAING URLS
    urls = []
    # Extract URLs from sitemaps
    if j == 1:
        url = "https://www.dinakaran.com/post-sitemap.xml"
    else:
        url = "https://www.dinakaran.com/post-sitemap" + str(j) + ".xml"
    print("Extracting from: ", url)
    reqs = requests.get(url, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    #print(soup)
    for link in soup.findAll('loc'):
        urls.append(link.text)
    #for link in soup.find_all('a'):
    #    urls.append(link.get('href')) 
    print("URLs so far: ",len(urls))

    # STEP 2: CLEAN URLS
    # deduplication:
    dedup_url = list(set(urls))
    # delete from the list any article from unwanted section
    # -> No need because you cannot identify sections based on the urls of articles.

    # STEP 3: SCRAPE
    print("Total number of USABLE urls found: ", len(dedup_url))

    ## INSERTING IN THE DB:
    url_count = 0
    for url in dedup_url:
        if url == "":
            pass
        else:
            if url == None:
                pass
            else:
                if "dinakaran.com" in url:
                    print(url, "FINE")
                    ## SCRAPING USING NEWSPLEASE:
                    try:
                        response = requests.get(url, headers=headers)
                        # process
                        article = NewsPlease.from_html(response.text, url=url).__dict__
                        # add on some extras
                        article['date_download']=datetime.now()
                        article['download_via'] = "Direct2"
                        article['source_domain'] = source
                        article['language'] = "ta"
                        
                        ## Fixing Date & Title & Main Text
                        soup = BeautifulSoup(response.content, 'html.parser')

                        # Title:
                        article['title'] = dinakarancom_story(soup)['title']

                        # Text:
                        article['maintext'] = dinakarancom_story(soup)['maintext']

                        # Date: 
                        article['date_publish'] = dinakarancom_story(soup)['date_publish']

                        ## Inserting into the db
                        try:
                            year = article['date_publish'].year
                            month = article['date_publish'].month
                            colname = f'articles-{year}-{month}'
                        except:
                            colname = 'articles-nodate'

                        try:
                            # Inserting article into the db:
                            db[colname].insert_one(article)
                            # count:
                            url_count = url_count + 1
                            print("+ Date published: ", article['date_publish'], " + TITLE :",article['title'][0:20],"+ TEXT :",article['maintext'][0:30])
                            print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        except DuplicateKeyError:
                            print("DUPLICATE! Not inserted.")
                    except Exception as err: 
                        print("ERRORRRR......", err)
                        pass
                else:
                    pass

    print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")



