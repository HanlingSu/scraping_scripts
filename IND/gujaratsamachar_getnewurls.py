#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Jun 8 2023

@author: diegoromero

This script updates gujaratsamachar.com using daily sitemaps
It can be run as often as one desires. 

Sitemaps:
https://www.gujaratsamachar.com/sitemap.xml

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

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## NEED TO DEFINE SOURCE!
source = 'gujaratsamachar.com'

## STEP 0: Get sitemap urls:
siteurls = []
url = "https://www.gujaratsamachar.com/sitemap.xml"
reqs = requests.get(url, headers=headers)
soup = BeautifulSoup(reqs.text, 'html.parser')
for link in soup.findAll('loc'):
    if ".xml" in link.text:
        siteurls.append(link.text)
    else:
        pass

# Cleaning sitemaps:
blpatterns = ['/photo/','/static-page/','/sahiyar/','/shatdal/','/dharmlok/','/chitralok/','/zagmag/','/food/','/cine-magic/','/tantri-lekh/','/prasangpat/','/sports/','/health/','/lifestyle-fashion/','/relationship/','/entertainment/','/video/']
list_siteurls = []
for url in siteurls:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            count_patterns = 0
            for pattern in blpatterns:
                if pattern in url:
                    count_patterns = count_patterns + 1
            if count_patterns == 0:
                list_siteurls.append(url)

print("--> ",len(list_siteurls), " sitemaps found.")
#for link in soup.find_all('a'):
#    urls.append(link.get('href')) 

########################################
##            Custom parser           ##   
########################################
def gujaratsamacharcom_story(soup):
    """
    Function to pull the information we want from gujaratsamachar.com stories
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
            hold_dict['title']  = article_title = None

    # Get Main Text:   
    try:
        listoftexts = soup.findAll("p")
        if len(listoftexts) > 2:
          text = listoftexts[2].text + " " + listoftexts[3].text
        else:
          text = listoftexts[2].text
        text = text.strip()
        hold_dict['maintext'] = text
    except:
        hold_dict['maintext'] = None  

    # Get Date
    try:
        span_tags = soup.find('div', {'class': 'detail-news article-detail-news'}).find('p', {'class': 'text-muted'}).text.replace("Updated: ","")
        date = dateparser.parse(span_tags, date_formats=['%Y-%m-%d %H:%M:%S'])
        hold_dict['date_publish'] = date
    except :
        hold_dict['date_publish'] = None
    
    return hold_dict
########################################


# Scraping articles from each sitemap:
for stm in list_siteurls:
    urls = []
    reqs = requests.get(stm, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    for link in soup.findAll('loc'):
        urls.append(link.text)

    print("--> ",len(urls), " urls found.")

    # STEP 1: Get rid or urls from blacklisted sources
    # List of unique urls:
    dedup_urls = list(set(urls))

    blpatterns = ['/photo/','/static-page/','/sahiyar/','/shatdal/','/dharmlok/','/chitralok/','/zagmag/','/food/','/cine-magic/','/tantri-lekh/','/prasangpat/','/sports/','/health/','/lifestyle-fashion/','/relationship/','/entertainment/','/video/']
    list_urls = []
    for url in dedup_urls:
        if url == "":
            pass
        else:
            if url == None:
                pass
            else:
                count_patterns = 0
                for pattern in blpatterns:
                    if pattern in url:
                        count_patterns = count_patterns + 1
                if count_patterns == 0:
                    list_urls.append(url)

    print("Total number of USABLE urls found: ", len(list_urls), ".")

    ## INSERTING IN THE DB:
    url_count = 0
    for url in list_urls:
        if url == "":
            pass
        else:
            if url == None:
                pass
            else:
                if 'gujaratsamachar.com' in url:
                    print("+ URL: ", url)
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
                        article['source_domain'] = 'gujaratsamachar.com'
                        
                        ## Fixing Date, Title, and Text
                        soup = BeautifulSoup(response.content, 'html.parser')

                        # Title:
                        article['title'] = gujaratsamacharcom_story(soup)['title']

                        # Text:
                        article['maintext'] = gujaratsamacharcom_story(soup)['maintext']

                        # Date: 
                        article['date_publish'] = gujaratsamacharcom_story(soup)['date_publish']
                        # #print(article_date)

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
                            #print(article['date_publish'].month)
                            print("+ TITLE: ", article['title'][0:80])
                            print("+ TEXT: ", article['maintext'][0:100])
                            print("+ DATE: ", article['date_publish'])
                            print("+ Inserted: ", colname, " - number of urls so far: ", url_count, " from: ",stm)
                        except DuplicateKeyError:
                            print("DUPLICATE! Not inserted.")
                    except Exception as err: 
                        print("ERRORRRR......", err)
                        pass
                else:
                    pass

    print("Done inserting ", url_count, " manually collected urls from ", stm)