#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Jan 7 2023

@author: diegoromero

This script updates caravan.kz using sitemaps. 
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
uri = 'mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true'
db = MongoClient(uri).ml4p
#db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
#db = MongoClient('mongodb://ml4pAdmin:ml4peace@research-devlab-mongodb-01.oit.duke.edu').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

###########################################################
def caravankz_story(soup):
    """
    Function to pull the information we want from caravan.kz stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}

    # Get Title: 
    try:
        article_title = soup.find("title").text
        hold_dict['title']  = article_title   
    except:
        hold_dict['title']  = None
        
    # Get Main Text:
    try:
        text = soup.find("div", {"class":"full-article__text clear"}).text
        text = text.replace("\xa0", "")
        text = text.replace("\n", " ")
        hold_dict['maintext'] = text
    except:
        hold_dict['maintext'] = None  

    # Get Date
    try:
        datebitx = soup.find("time", {"class":"full-breadcrumb__time"}).text
        #print(datebitx)
        datevector = datebitx.split()
        dayx = int(datevector[0])
        
        containsdate = soup.find("script",{"type":"text/javascript"})
        containsdate = str(containsdate)
        vectordate = containsdate.split()
        for x in vectordate:
          if "Date" in x:
            indexp = vectordate.index(x)
            datebit = vectordate[indexp+1]
            datebit = datebit.replace('-',' ')
            datebit = datebit.replace("'","")
            vecdatebit = datebit.split()
            monthn = int(vecdatebit[0])
            yearn = int(vecdatebit[1])

        article_date = datetime(int(yearn),int(monthn),int(dayx))
        hold_dict['date_publish'] = article_date
    except:
        try:
            datebit = soup.find("time", {"class":"full-breadcrumb__time"}).text
            datebit = datebit.replace(".", " ")
            datevector = datebit.split()
            dayx = datevector[0]
            monthx = datevector[1]
            yearx = datevector[2]
            article_date = datetime(int(yearx),int(monthx),int(dayx))
            hold_dict['date_publish'] = article_date
        except:
            hold_dict['date_publish'] = None
   
    return hold_dict 
###########################################################

## COLLECTING URLS
## NEED TO DEFINE SOURCE!
source = 'caravan.kz'

urls = []
# STEP 1: Get urls of articles from sitemaps:
#for sitmp in siteurls:
for j in range(1,320):
    sitmp = "https://www.caravan.kz/news/page/" + str(j) + "/"
    print("Extracting from: ", sitmp)
    reqs = requests.get(sitmp, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    #for link in soup.findAll('loc'):
    #    urls.append(link.text)
    for link in soup.find_all('div', {'class' : 'BlockNewsCardImage'}):
        urls.append(link.find('a')['href']) 
    print("URLs so far: ", len(urls))


# STEP 2: Get rid or urls from blacklisted sources
blpatterns = ['/sport/','/info/','/tag/']

clean_urls = []
for url in urls:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if "caravan.kz" in url:
                count_patterns = 0
                for pattern in blpatterns:
                    if pattern in url:
                        count_patterns = count_patterns + 1
                if count_patterns == 0:
                    clean_urls.append(url)
            else:
                newurl = "https://www.caravan.kz" + url 
                clean_urls.append(newurl)
# List of unique urls:
final_result = list(set(clean_urls))

print("Total number of USABLE urls found: ", len(final_result))


## INSERTING IN THE DB:
url_count = 0
processed_url_count=0
for url in final_result:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if "caravan.kz" in url:
                print("+ URL: ",url, " - from Page: ", str(j))
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
                    
                    ## Fixing main texts when needed:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Get Main Text:
                    # article['maintext'] = caravankz_story(soup)['maintext']

                    # Get Title
                    # article['title'] = caravankz_story(soup)['title']

                    #Date:
                    # article['date_publish'] = caravankz_story(soup)['date_publish']
                    #time.sleep(40)

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
                        print("+ article Title: ", article['title'][0:50])
                        print("+ article Text: ", article['maintext'][0:100])
                        print("+ article Date: ", article['date_publish'])
                        print("+ Inserted! in ", colname, " - number of urls so far: ", url_count)
                        #db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        print("DUPLICATE! not inserted.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
                processed_url_count += 1
                print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

            else:
                pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")