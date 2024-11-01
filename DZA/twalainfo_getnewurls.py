#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 2023

@author: diegoromero

This script updates twala.info using sections.

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

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## NEED TO DEFINE SOURCE!
source = 'twala.info'

# Custom Parser

##

##
# Sections
sections = ["category/a-chaud-actualite-algerienne/","format/fil_actualite/","category/business/","category/societe/"]
endnumb = [10,253,2,8]
#60, 1518, 12, 48
#https://twala.info/fr/category/a-chaud-actualite-algerienne/
#https://twala.info/fr/category/a-chaud-actualite-algerienne/?offset=18 (60)
#https://twala.info/fr/format/fil_actualite/?offset=6
#https://twala.info/fr/format/fil_actualite/?offset=1518
#https://twala.info/fr/category/business/?offset=12
#https://twala.info/fr/category/societe/?offset=48

for sect in sections:
    time.sleep(1)
    ## STEP 1: COLLECTING URLS
    urls = []
    indexsect = sections.index(sect)
    numberx = endnumb[indexsect]
    for i in range(0,int(numberx)+1):
        if i == 0:
            url = "https://twala.info/fr/" + sect
        else:
            pagen = i*6
            url = "https://twala.info/fr/" + sect + "?offset=" + str(pagen)

        print("Extracting from ", url)

        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        for link in soup.find_all('a'):
            urlx = link.get('href')
            urls.append(urlx) 

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
                if "https://twala.info/" in url:
                    ## SCRAPING USING NEWSPLEASE:
                    try:
                        # count:
                        url_count = url_count + 1
                        #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
                        header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                        response = requests.get(url, headers=header)
                        # process
                        article = NewsPlease.from_html(response.text, url=url).__dict__
                        # add on some extras
                        article['date_download']=datetime.now()
                        article['download_via'] = "Direct2"
                        article['source_domain'] = source
                        
                        ## Fixing main texts when needed:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Title:
                        #article['title'] = timesofindia_story(soup)['title']

                        # Main Text
                        try:
                            maintext = soup.find('meta', {'property' : 'og:description'})['content']
                            article['maintext'] = maintext
                        except:
                            article['maintext'] = soup.find('p', {'class' : 'my-4'}).text
                            article['maintext'] = maintext

                        # article['maintext'] = timesofindia_story(soup)['maintext']
                        print('newsplease maintext', article['maintext'][:50])

                        # Date of Publication
                        #article['date_publish'] = timesofindia_story(soup)['date_publish']

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
                            myquery = { "url": url, "source_domain" : 'web.archive.org'}

                            db[colname].delete_one(myquery)
                            pogressm = url_count/len(list_urls)
                            print("DUPLICATE! Not inserted. --> Progress:", str(pogressm))
                    except Exception as err: 
                        print("ERRORRRR......", err)
                        #pass
                else:
                    pass


    print("Done inserting ", url_count, " manually collected urls from ",  source)
    time.sleep(2)


