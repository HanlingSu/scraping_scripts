#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on jan 5 2023

@author: diegoromero

This script updates bbc.com using daily sitemaps.It can be run at any time,
to make sure we have obtained as many URLs as we could have.
 
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
uri = 'mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true'
db = MongoClient(uri).ml4p
#db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
#db = MongoClient('mongodb://ml4pAdmin:ml4peace@research-devlab-mongodb-01.oit.duke.edu').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


## COLLECTING URLS
urls = []
siteurls = []

## NEED TO DEFINE SOURCE!
source = 'bbc.com'

# STEP 0: Get sitemap urls:
url = "https://www.bbc.com/sitemaps/https-sitemap-com-news-1.xml"
print("Extracting from: ", url)
reqs = requests.get(url, headers=headers)
soup = BeautifulSoup(reqs.text, 'html.parser')
for link in soup.findAll('loc'):
    siteurls.append(link.text)
siteurls = list(set(siteurls))
#for link in soup.find_all('a'):
#    urls.append(link.get('href')) 
print("Number of sitemaps found: ", len(siteurls))
siteurls

# STEP 1: Get urls of articles from sitemaps:
for sitmp in siteurls:
    counter = 0
    urls = []
    while True:
        counter = counter + 1
        if counter == 1:
            newurl = sitmp
        else:
            newurl = sitmp + "?page=" + str(counter)
        print("Scraping this URL: ", newurl)
        req = requests.get(newurl, headers = headers)
        #soup = BeautifulSoup(req.content, 'html.parser')
        soup = BeautifulSoup(req.text, 'html.parser')
  
        texts = soup.findAll("time")
        if len(texts) == 0:
            break
        else:
            for i in texts:
                print(i)
                position1 = str(i).find("2024-8")
                position2 = str(i).find("2024-9")
            for link in soup.find_all('a'):
                urls.append(link.get('href')) 
            if position1 <0 and position2 <0:
                break    
        #print(len(urls))
    readyurls = []
    for url in urls:
        if ".com/" in url:
            readyurls.append(url)
        else:
            pass
    print("Number of URLs obtained: ",len(readyurls))

    # STEP 2: Get rid or urls from blacklisted sources
    blpatterns = ['/sport/', '/travel/', '/culture/', '/sport-', '/multimedia/', '/learningenglish/', '/bbc_arabic_radio/', '/arts/', '/naidheachdan/', '/av/']

    clean_urls = []
    for url in readyurls:
        count_patterns = 0
        for pattern in blpatterns:
            if pattern in url:
                count_patterns = count_patterns + 1
        if count_patterns == 0:
            clean_urls.append(url)

    # List of unique urls:
    list_urls = list(set(clean_urls))

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
                if "bbc.com" in url:
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
                        
                        ## Fixing main texts when needed:
                        soup = BeautifulSoup(response.content, 'html.parser')

                        # Get Main Text:
                        if article['maintext'] == None:
                            try:
                                soup.find('div', {'aria-live' : "polite"}).find_all('p')
                                maintext = ""
                                for i in  soup.find('div', {'aria-live' : "polite"}).find_all('p'):
                                    maintext += i.text
                                article['maintext'] = maintext
                            except:
                                try:
                                    soup.find('main', {'role':'main'}).find_all('p')
                                    maintext = ""
                                    for i in soup.find('main', {'role':'main'}).find_all('p'):
                                        maintext += i.text
                                    article['maintext'] = maintext
                                except:
                                    try:
                                        soup.find_all('div', {'data-component': "text-block"})
                                        maintext = ""
                                        for i in soup.find_all('div', {'data-component' : "text-block"}):
                                            maintext+= i.find('p').text
                                        article['maintext'] = maintext
                                    except:
                                        try:
                                            soup.find_all('p', {'class' : "ssrcss-1q0x1qg-Paragraph eq5iqo00"})
                                            maintext = ""
                                            for i in soup.find_all('p', {'class' : "ssrcss-1q0x1qg-Paragraph eq5iqo00"}):
                                                maintext+= i.text
                                            article['maintext'] = maintext
                                        except:
                                            maintext = None
                                            article['maintext'] = None

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
                            db[colname].insert_one(article)
                            # count:
                            url_count = url_count + 1
                            #print(article['date_publish'].month)
                            #print(article['title'][0:200])
                            #print(article['maintext'][0:200])
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