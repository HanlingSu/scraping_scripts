#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 23, 2022

@author: diegoromero

This script updates elpais.com using queries per section. 
This script can be ran whenever needed (just make the necessary modifications).
 
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

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
#db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
#db = MongoClient('mongodb://ml4pAdmin:ml4peace@research-devlab-mongodb-01.oit.duke.edu').ml4p


# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


## NEED TO DEFINE SOURCE!
source = 'elpais.com'

# STEP 1: Extracting urls from key sections:

sections = ['noticias/europa','noticias/estados-unidos','noticias/mexico','noticias/latinoamerica','noticias/oriente-proximo','noticias/asia','noticias/africa','economia']
number = ['4','13','24','50','2','2','4','1']
#number = ['44','44','44','44','20','22','30','42']

year_up = 2024
month_up = 9

for sect in sections:
    time.sleep(2)
    ## COLLECTING URLS
    urls = []
    indexsect = sections.index(sect)
    numberx = number[indexsect]
    for i in range(0,int(numberx)+1):
        url = "https://elpais.com/" + sect + "/" + str(i) + "/"

        print("Extracting from ", url)

        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        for link in soup.find_all('a'):
            urlx = "https://elpais.com" + link.get('href')
            urls.append(urlx) 

        print("+ Number of urls so far: ", len(urls))

    # Manually check urls:
    #dftest = pd.DataFrame(list_urls)  
    #dftest.to_csv('/Users/diegoromero/Downloads/test.csv')  

    # STEP 2: Get rid or urls from blacklisted sources
    blpatterns = ['/opinion/', '/subscriptions/', '/television/', '/deportes/']

    # List of unique urls:
    dedup = list(set(urls))
    list_urls = []

    for url in dedup:
        if url == None:
            pass
        else:
            if url == "":
                pass
            else:
                if ".comhttps://" in url:
                    deletebitlen = len("https://elpais.com")
                    urlcorrect = url[deletebitlen:]
                else:
                    urlcorrect= url 
                count_patterns = 0
                for pattern in blpatterns:
                    if pattern in url:
                        count_patterns = count_patterns + 1
                if count_patterns == 0:
                    list_urls.append(urlcorrect)

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
                if 'elpais.com' in url:
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
                        article['source_domain'] = 'elpais.com' 
                        article['language'] = 'es'

                        
                        ## Fixing Date, Main Text and Title:
                        response = requests.get(url, headers=header).text
                        soup = BeautifulSoup(response)

                        ## Date
                        if article['date_publish'] == None:
                            try: 
                                contains_date = soup.find("meta", {"property":"article:published_time"})
                                contains_date = contains_date['content']
                                article_date = dateparser.parse(contains_date,date_formats=['%d/%m/%Y'])
                                article['date_publish'] = article_date  
                            except:
                                article['date_publish'] = None

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
                                if article['date_publish'].year == year_up:
                                    if article['date_publish'].month >= month_up:
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
                                        print("Wrong month",article['date_publish'])
                                else:
                                    print("Wrong year",article['date_publish'])
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
