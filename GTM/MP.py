#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on July 28, 2023

@author: diegoromero

This script scrapes the institutional website of the ministerio publico.
 
"""
# Packages:
import time
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


##
def mp_story(soup):
    """
    Function to pull the information we want from MP stories
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
        sentences = soup.findAll("p") 
        text = ""
        for sent in sentences:
            text = text + sent.text
        text = text.strip()
        hold_dict['maintext'] = text
    except:
        hold_dict['maintext'] = None

    # Get Date
    try:
        monthNames = ["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"]

        containsdate = soup.find("h6").text
        containsdate = containsdate.lower()
        vectordate = containsdate.split()

        # day, month, year:
        daystr = vectordate[2]
        monthname = vectordate[3]
        yearstr = vectordate[4]

        monthstr = 1 + monthNames.index(monthname)

        article_date = datetime(int(yearstr),int(monthstr),int(daystr))
        hold_dict['date_publish'] = article_date
    except Exception as err:
        hold_dict['date_publish'] = None
        #print("Error when trying to get the date", err)

    return hold_dict
##

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
#db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
#db = MongoClient('mongodb://ml4pAdmin:ml4peace@research-devlab-mongodb-01.oit.duke.edu').ml4p


# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## NEED TO DEFINE SOURCE!
source = 'mp.gob.gt'

# STEP 1: Extracting urls from key sections:
urls = []

for i in range(1,int(1686)+1):
    if i == 1:
        url = "https://www.mp.gob.gt/noticias/"
    else:
        url = "https://www.mp.gob.gt/noticias/page/" + str(i) + "/"
    
    print("Extracting from ", url)
    time.sleep(1)
    ## COLLECTING URLS
    reqs = requests.get(url, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    for link in soup.find_all('a'):
        urls.append(link.get('href')) 

    print("+ Number of urls so far: ", len(urls))

# Deduplicate URL list
list_urls = list(set(urls))
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
            if 'mp.gob.gt' in url:
                print(url, "FINE")
                time.sleep(1)
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
                    article['source_domain'] = 'mp.gob.gt' 
                    article['language'] = 'es'

                    
                    ## Fixing Date, Main Text and Title:
                    response = requests.get(url, headers=header).text
                    soup = BeautifulSoup(response)

                    # Title:
                    article['title'] = mp_story(soup)['title']

                    # Main Text
                    article['maintext'] = mp_story(soup)['maintext']

                    # Date of Publication
                    article['date_publish'] = mp_story(soup)['date_publish']

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
                        if colname != 'articles-nodate':
                            # Inserting article into the db:
                            db[colname].insert_one(article)
                            # count:
                            url_count = url_count + 1
                            #print(article['date_publish'])
                            print("Title: ", article['title'][0:25]," + Main Text: ", article['maintext'][0:30])
                            #print(article['maintext'])
                            print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                            #db['urls'].insert_one({'url': article['url']})
                        else:
                            print("No Date",url)
                    except DuplicateKeyError:
                        print("DUPLICATE! Not inserted.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
            else:
                pass


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
