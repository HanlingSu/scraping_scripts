#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Nov 11 2021

@author: diegoromero

This script updates theguardian.com using daily sitemaps.
It MUST BE RUN EVERY DAY.
 
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
source = 'theguardian.com'
## Define YEAR and MONTH to update:
year_up = 2024
month_up = 9

# YEAR:
yearn = "/" + str(year_up) + "/"
print(yearn)

# STEP 0: Get articles from sections:
# sections:
sections = ['uk-news','world','environment','business','world/americas','world/middleeast','world/europe-news','us-news']
# CHANGE endnumbers for each section in accordance with how far 
# back you need to go:
endnumber = ['105','85','45','40','15','13','38','70'] 

for section in sections:
    indexword = sections.index(section)
    endnumberx = endnumber[indexword]

    for i in range(1, int(endnumberx)+1):
        if i == 1:
            url = "https://www.theguardian.com/" + section
            #+ ".aspx"   
        else:
            url = "https://www.theguardian.com/" + section + "?page=" + str(i) 
        
        print("Section: ", section, " -> URL: ", url)

        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        for link in soup.find_all('a'):
            lk = "https://www.theguardian.com" + link.get('href')
            urls.append(lk) 
        print("URLs so far: ", len(urls))

#dftest = pd.DataFrame(urls)  
#dftest.to_csv('/Users/diegoromero/Downloads/test.csv') 

# STEP 0: hourly sitemap:
#url = "https://www.theguardian.com/sitemaps/news.xml"
#print("Extracting from: ", url)
#reqs = requests.get(url, headers=headers)
#soup = BeautifulSoup(reqs.text, 'html.parser')
#for link in soup.findAll('loc'):
#    siteurls.append(link.text)
#for link in soup.find_all('a'):
#    urls.append(link.get('href')) 

#dftest = pd.DataFrame(siteurls)  
#dftest.to_csv('/Users/diegoromero/Downloads/test.csv')  

# STEP 2: Get rid or urls from blacklisted sources
blpatterns = ['/lifeandstyle/', '/music/', '/tv-and-radio/', '/games/', '/artanddesign/', '/film/', '/sport/', '/fashion/', '/football/', '/stage/', '/books/', '/music/', '/commentisfree/', '/food/', '/fashion/', '/recipes/', '/travel/', '/amp', '/advertiser-content/', '/employer/', '/advertising', '/arts', '/crosswords', '/acivate/', '/images/', '/a-journey-to-carbon-neutral-coffee/', '/guardian-masterclasses/', '/artanddesign/', '/video/', '/all-in-all-together/', '/gallery/', '/info/', '/datablog/', '/live/', '/ng-interactive/', '/animals-farmed/', '/american-express-business-class/', '/with-you-all-the-way/', '/shortcuts/', '/membership/', '-datablog/', '/backing-our-communities/', '/bank-australia-people-australia-needs/', '/blue-cheese-every-day/', '/brighter-mornings/', '/british-cider-time/', '/brother-doing-business-well/', '/postcolonial-blog/', '/series/', '/getting-back-on-track/', '/greener-grapes/', '/gnm-press-office/', '/lets-live-clean/', '/from-the-archive-blog/']

clean_urls = []
for url in urls:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if "theguardian.com" in url:
                count_patterns = 0
                for pattern in blpatterns:
                    if pattern in url:
                        count_patterns = count_patterns + 1
                if count_patterns == 0:
                    clean_urls.append(url)

# List of unique urls:
list_urls = list(set(clean_urls))
print("Total number of USABLE urls found: ", len(list_urls))

#dftest = pd.DataFrame(list_urls)  
#dftest.to_csv('/Users/diegoromero/Downloads/test.csv')  

## INSERTING IN THE DB:
url_count = 0
for url in list_urls:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if "theguardian.com" in url:
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