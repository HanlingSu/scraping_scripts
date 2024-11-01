#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Aug 29 2022

@author: diegoromero

This script updates maliactu.net scraping each section of the site.
It can be run as often as one desires. 
 
"""
# Packages:
import random
import sys
from this import d
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

import time

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p


# headers for scraping
#headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}
#headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Safari/605.1.15 Version/13.0.4'}
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
#headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}

## NEED TO DEFINE SOURCE!
source = 'maliactu.net'

# Sections -> need to define enpage for each of the sections
sections = ["gouvernement", "tv", "politique", "mali-infos-de-dernieres-minutes", "breves-du-mali", "afrique-2"]
endpage = ["237","1884","552","445", "1374", "1200"]


for section in sections:
    urls =[]
    enpagen = endpage[sections.index(section)]
    print(enpagen)
    for i in range(1,int(enpagen)+1):
        if i == 1:
            url = "https://maliactu.net/category/" + section + "/"
        else:
            url = "https://maliactu.net/category/" + section + "/page/" + str(i) + "/"

        print("Extracting from: ", url)
        time.sleep(1)
        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')
        #print(soup)
        #for link in soup.findAll('loc'):
        #    urls.append(link.text)
        smapurls = []
        for link in soup.find_all('a'):
            urls.append(link.get('href')) 
            smapurls.append(link.get('href')) 
        print("URLs so far: ", len(urls))
 
    # STEP 1: Get rid or urls from blacklisted sources
    clean_urls = []
    for url in urls:
        if url == "":
            pass
        else:
            if url == None:
                pass
            else:
                try: 
                    clean_urls.append(url)
                except:
                    pass

    # List of unique urls:
    list_urls = list(set(clean_urls))

    # Manually check urls:
    #list_urls = list(set(urls))
    #dftest = pd.DataFrame(list_urls)  
    #dftest.to_csv('/Users/diegoromero/Downloads/test.csv')  

    print("Total number of USABLE urls found for ", section, " is: ", len(list_urls))

    ## INSERTING IN THE DB:
    url_count = 0
    for url in list_urls:
        if url == "":
            pass
        else:
            if url == None:
                pass
            else:
                if "maliactu.net" in url:
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
                        article['language'] = 'fr'
                    
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
                            #print(article['title'])
                            #print(article['maintext'])
                            print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                            db['urls'].insert_one({'url': article['url']})
                        except DuplicateKeyError:
                            print("DUPLICATE! Not inserted.")
                            #print("Duplicated, but fixing:")
                            # Delete previous record:
                            #myquery = { "url": url}
                            #db[colname].delete_one(myquery)
                            # Adding new record:
                            #db[colname].insert_one(article)
                            #url_count = url_count + 1
                            #print("TEXT: ",article['maintext'][0:30]," + Title: ",article['title'][0:10])
                            #print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                            #db['urls'].insert_one({'url': article['url']})
                    except Exception as err: 
                        print("ERRORRRR......", err)
                        pass
                else:
                    pass

    print("Done inserting ", url_count, " manually collected urls from ",  section, " into the db.")