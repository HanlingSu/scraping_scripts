#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Feb 2 2022

@author: diegoromero

This script updates iwpr.net using daily sitemaps.
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

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
#db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
#db = MongoClient('mongodb://ml4pAdmin:ml4peace@research-devlab-mongodb-01.oit.duke.edu').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


## COLLECTING URLS
urls = []

## NEED TO DEFINE SOURCE!
source = 'iwpr.net'

## Define YEAR and MONTH to update:
year_up = 2024
month_up = 8


## STEP 0: URLS FROM SITEMAP:
url = "https://iwpr.net/sitemap.xml"
reqs = requests.get(url, headers=headers)
soup = BeautifulSoup(reqs.text, 'html.parser')
for link in soup.find_all('a'):
    #urls.append(link.get('href')) 

## STEP 0: URLS FROM SECTIONS:
keywords = ['africa','asia','europe-eurasia','latin-america-caribbean','middle-east-north-africa']
endnumber = ['5','5','5','5','5']

for word in keywords:
    indexword = keywords.index(word)
    endnumberx = endnumber[indexword]

    for i in range(1, int(endnumberx)+1):
        if i == 1:
            url = 'https://iwpr.net/global-voices/' + word
        else:
            url = 'https://iwpr.net/global-voices/' + word + '?region=All&page=' + str(i) 
        
        print(url)

        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        for link in soup.find_all('a'):
            urls.append(link.get('href')) 
            
#https://iwpr.net/global-voices/africa?region=All&page=2
#https://iwpr.net/global-voices/asia?region=All&page=2
#https://iwpr.net/global-voices/europe-eurasia?region=All&page=2
#https://iwpr.net/global-voices/latin-america-caribbean
#https://iwpr.net/global-voices/middle-east-north-africa

## STEP 1: URLS FROM TOPICS

## TOPICS 
keywords = ['elections','war-crimes','conflict-resolution','human-rights','accountability','political-reform','health','international-justice','women','womens-rights','rule-law','civil-society','social-justice','regime','journalism','conflict','detentions','education','media','media-development','diplomacy','protests','refugees','coronavirus','economy']
endnumber = ['3','3','3','3','3','3','3','3','3','3','3','3','3','3','3','3','3','3','3','3','3','3','3','3','3']

for word in keywords:
    indexword = keywords.index(word)
    endnumberx = endnumber[indexword]

    for i in range(0, int(endnumberx)):
        if i == 0:
            url = 'https://iwpr.net/global-voices/topics/' + word
        else:
            url = 'https://iwpr.net/global-voices/topics/' + word + '?page=' + str(i) 
        
        print(url)

        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        for link in soup.find_all('a'):
            urls.append(link.get('href')) 


## STEP 2: URLS FROM COUNTRY SECTIONS (FOR COUNTRIES WITH THEIR OWN SECTION)
countrynames = ['ukraine','belarus','caucasus/armenia','caucasus/azerbaijan','caucasus/georgia','caucasus/karabakh','balkans/bosnia-and-herzegovina','moldova']
endnumber = ['2','3','3','3','3','3','3','3']

for country in countrynames:
    indexword = countrynames.index(country)
    endnumberx = endnumber[indexword]

    for i in range(0, int(endnumberx)):
        if i == 0:
            url = 'https://iwpr.net/global-voices/europe-eurasia/' + country
        else:
            url = 'https://iwpr.net/global-voices/europe-eurasia/' + country + '?page=' + str(i) 
        
        print(url)

        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        for link in soup.find_all('a'):
            urls.append(link.get('href')) 


## STEP 3: URLS FOR COUNTRIES WITHOUT THEIR OWN SECTION: SERBIA AND KOSOVO
countrynames = ['Serbia','Kosovo']
endnumber = ['3','3']

for country in countrynames:
    indexword = countrynames.index(country)
    endnumberx = endnumber[indexword]

    for i in range(0, int(endnumberx)):
        if i == 0:
            url = 'https://iwpr.net/search?keys=' + country + '&sort_bef_combine=created_DESC&locations=All&topics=All&year=&author=&type=All&format=All'
        else:
            url = 'https://iwpr.net/search?keys=' + country +  '&sort_bef_combine=created_DESC&locations=All&topics=All&year=&author=&type=All&format=All&sort_by=created&sort_order=DESC&page=' + str(i) 
        
        print(url)

        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        for link in soup.find_all('a'):
            urls.append(link.get('href')) 

## Preparing URLs for scraping:

# List of unique urls:
unique_urls = list(set(urls))

list_urls = []
for url in unique_urls:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if "https://iwpr.net/" in url:
                newurlx = url
            else:
                newurlx = "https://iwpr.net" + url
            #Appending url: 
            list_urls.append(newurlx) 
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
            if "iwpr.net" in url:
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
                    article['source_domain'] = "iwpr.net"
                    
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
                    # collection to update:
                    colname_update = f'articles-{year_up}-{month_up}'

                    try:
                        year = article['date_publish'].year
                        month = article['date_publish'].month
                        colname = f'articles-{year}-{month}'
                        #print(article)
                    except:
                        colname = 'articles-nodate'
                    try:
                        if colname == colname_update:
                        # Inserting article into the db:
                            db[colname].insert_one(article)
                            # count:
                            url_count = url_count + 1
                            print("+TITLE: ", article['title'][0:20], " +MAIN TEXT: ", article['maintext'][0:25])
                            print("Date extracted: ", article['date_publish'], " + Inserted! in ", colname, " - number of urls so far: ", url_count)
                            db['urls'].insert_one({'url': article['url']})
                        else:
                            if colname == 'articles-nodate':
                                # Inserting article into the db (articles-nodate collection):
                                db[colname].insert_one(article)
                                # count:
                                print("+TITLE: ", article['title'][0:20], " +MAIN TEXT: ", article['maintext'][0:25])
                                print("No date extracted. -> Inserted in ", colname)
                                db['urls'].insert_one({'url': article['url']})
                            else:
                                pass
                    except DuplicateKeyError:
                            print("DUPLICATE! Not inserted.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
            else:
                pass


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")