#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Feb 3 2022

@author: diegoromero

This script updates indiatimes.com using sitemaps.
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
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
#db = MongoClient('mongodb://ml4pAdmin:ml4peace@research-devlab-mongodb-01.oit.duke.edu').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
#headers = {'User-Agent': 'MachineLearningForPeaceBot/1.0 (+https://mlp.trinity.duke.edu/#en)'}


## COLLECTING URLS
urls = []

## NEED TO DEFINE SOURCE!
source = 'indiatimes.com'


# Check the sitemaps to determine the range:
# https://www.indiatimes.com/central-service/webstories/sitemap-index.xml
# https://www.indiatimes.com/central-service/hindi/webstories/sitemap-index.xml

## Hindi:
for j in range(1,3):
    # Extract URLs from sitemaps
    url = "https://www.indiatimes.com/hindi/central-service/webstories/sitemap-" + str(j) + ".xml"
    print("Extracting from: ", url)
    reqs = requests.get(url, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    #print(soup)
    for link in soup.findAll('loc'):
        urls.append(link.text)
    print("URLs so far: ",len(urls))
    #for link in soup.find_all('a'):
    #    urls.append(link.get('href')) 

## English
for j in range(1,5):
    # Extract URLs from sitemaps
    url = "https://www.indiatimes.com/central-service/webstories/sitemap-" + str(j) + ".xml"
    print("Extracting from: ", url)
    reqs = requests.get(url, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    #print(soup)
    for link in soup.findAll('loc'):
        urls.append(link.text)
    print("URLs so far: ",len(urls))
    #for link in soup.find_all('a'):
    #    urls.append(link.get('href')) 

# STEP 1: Get rid or urls from blacklisted sources
# List of unique urls:
dedup_url = list(set(urls))

blpatterns = ['/hardware/','/bollywood/', '/life-and-style/', '/food/', '/beauty/', '/football/', '/racing/', '/auto/', '/relationships/', '/mobile/', '/cricket/', '/swimming/', '/travel/', '/olympics/', '/tech-and-auto/', '/tv/', '/wild-and-wacky/', '/art-and-culture/', '/others/', '/apps/', '/luxury/', '/gaming/', '/hockey/', '/sports/', '/golf/', '/fashion/', '/cars/', '/tennis/', '/movies-and-entertainment/', '/mma/', '/upcoming-gadgets/', '/tech-know/', '/basketball/', '/gadgets/', '/lifestyle/','/culture/', '/entertainment/', '/weird/']
list_urls = []
for url in dedup_url:
    if "indiatimes.com" in url:
        count_patterns = 0
        for pattern in blpatterns:
            if pattern in url:
                count_patterns = count_patterns + 1
        if count_patterns == 0:
            list_urls.append(url)
        else:
            pass

# Manually check urls:
#list_urls = list(set(urls))
#dftest = pd.DataFrame(list_urls)  
#dftest.to_csv('/Users/diegoromero/Downloads/test.csv')  

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
            if "indiatimes.com" in url:
                print(url, "FINE")
                ## SCRAPING USING NEWSPLEASE:
                try:
                    #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
                    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                    #header = {'User-Agent': 'MachineLearningForPeaceBot/1.0 (+https://mlp.trinity.duke.edu/#en)'}
                    response = requests.get(url, headers=header)
                    # process
                    article = NewsPlease.from_html(response.text, url=url).__dict__
                    # add on some extras
                    article['date_download']=datetime.now()
                    article['download_via'] = "Direct2"
                    article['source_domain'] = "indiatimes.com"
                    if "/hindi/" in url:
                        article['language'] = "hi"
                    else:
                        article['language'] = "en"
                    
                    ## Fixing Date:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    try: 
                        dateplace = soup.find("meta", {"property":"article:published_time"})
                        #<meta data-rh="true" property="article:published_time" content="Thu, 12 Jan 2012 06:21:25 GMT
                        contains_date = str(dateplace["content"])
                        months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

                        for monthx in months:
                            if monthx in contains_date:
                                # MONTH:
                                monthn = int(months.index(monthx)+1)
                        if monthn > 0:
                            # DAY:
                            indexm = contains_date.index(monthx)
                            dayn = int(contains_date[indexm-3:indexm-1])
                            # YEAR:
                            yearn = int(contains_date[indexm+4:indexm+8])
                            article['date_publish'] = datetime(int(yearn),int(monthn),int(dayn))
                    except:
                        datepublished = article['date_publish']
                        article['date_publish'] = datepublished

                    # Fixing Title:
                    try:
                        contains_title = soup.find("meta", {"property":"og:title"})
                        title = contains_title["content"]
                        article['title'] = title
                    except:
                        title = article['title']
                        article['title'] = title

                    # Fixing Main Text
                    try:
                        maintext = soup.findAll("p")[0].text
                        article['maintext'] = maintext 
                    except:
                        maintext = article['maintext']
                        article['maintext'] = maintext

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
                        print("Date published: ", article['date_publish'])
                        #print(article['date_publish'].month)
                        #print(article['title'][0:100])
                        #print(article['maintext'][0:100])
                        print("+ TITLE :",article['title'][0:20],"+ TEXT :",article['maintext'][0:30])
                        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        myquery = { "url": url}
                        db[colname].delete_one(myquery)
                        # Inserting article into the db:
                        db[colname].insert_one(article)
                        # count:
                        url_count = url_count + 1
                        print("Date published: ", article['date_publish'])
                        print("+ TITLE :",article['title'][0:20],"+ TEXT :",article['maintext'][0:30])
                        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        print("It was a duplicate!")
                        #db['urls'].insert_one({'url': article['url']})
                        #print("DUPLICATE! Not inserted.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
            else:
                pass


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")