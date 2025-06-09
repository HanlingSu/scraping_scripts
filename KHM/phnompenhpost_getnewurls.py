#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Nov 27 2021

@author: diegoromero

This script updates phnompenhpost.com using historical sitemaps.
It can be run whenever necessary. 
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
from newsplease import NewsPlease
from dotenv import load_dotenv
from bs4 import BeautifulSoup
# %pip install dateparser
import dateparser
import pandas as pd
import cloudscraper

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)

hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


## COLLECTING URLS
urls = []
siteurls = []

## NEED TO DEFINE SOURCE!
source = 'phnompenhpost.com'

# FOR UPDATING, CHOOOSE WHETHER TO USE SITEMAP (TIME CONSUMING) OR KEYWORD QUERIES

# STEP 0: Get urls from sections (KEYWORD QUERIES)
# keywords = ['politics-0','business','national','international','around-ngos']
# endnumber = ['10','100','120','80','20']


# for keyword in keywords:
#     keywordindex = keywords.index(keyword)
#     endnumberx = int(endnumber[keywordindex])+1
#     for i in range(0,endnumberx):
#         if i == 0:
#             url = "https://www.phnompenhpost.com/" + keyword 
#         else:
#             url = "https://www.phnompenhpost.com/" + keyword + "?page=" + str(i)

#         print("Extracting from: ", url)
#         reqs = requests.get(url, headers=headers)
#         soup = BeautifulSoup(reqs.text, 'html.parser')
#         #for link in soup.findAll('loc'):
#         #    urls.append(link.text)
#         for link in soup.find_all('a'):
#             urls.append(link.get('href')) 
#         print("URLs so far: ", len(urls))


# keywords = ['national','business', 'international']

# start_page = [ 1, 1, 1 ]
# end_page = [100, 1, 1]

# for k, sp, ep in zip (keywords, start_page, end_page):
#     for i in range(sp, ep+1):
#         url = 'https://www.phnompenhpost.com/' + k + '?page=' + str(i)
        
#         reqs = requests.get(url, headers=headers)
#         soup = BeautifulSoup(reqs.text, 'html.parser')
       
#         items = soup.find_all('div', {'class' : 'more-text'})
       
#         for item in items:
#             urls.append(item.find('a')['href'])
       
#         print("URLs so far: ", len(urls))



list_urls = pd.read_csv('/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/KHM/phnompenhpost.csv')['0']
print(len(list_urls))
print("Total number of USABLE urls found: ", len(list_urls))




## INSERTING IN THE DB:
url_count = 0
processed_url_count = 0
for url in list_urls:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if "phnompenhpost.com" in url:
                print(url, "FINE")
                ## SCRAPING USING NEWSPLEASE:
                try:
                    #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
                    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                    # process
                    article = NewsPlease.from_html(scraper.get(url).text).__dict__
                    # add on some extras
                    article['date_download']=datetime.now()
                    article['download_via'] = "Direct2"
                    article['source_domain'] = source
                    article['url'] = url

                    print("newsplease title: ", article['title'])
                    
                    ## Fixing Date:
                    soup = BeautifulSoup(scraper.get(url).text)

                    try:
                        date = soup.find('div', {'class' : 'ads-social-left-title'}).text.split('date ')[1].split('\n', 1)[0]
                        article['date_publish'] =  dateparser.parse(date)
                    except:
                        date = soup.find('div', {'class' : 'ads-social-left-title'}).text.split('date ')[1].split('ICT', 1)[0]
                        article['date_publish'] =  dateparser.parse(date)
                    print("newsplease date: ", article['date_publish'])

                    try:
                        maintext = '' 
                        for i in soup.find('div', {'id' : 'ArticleBody'}).find_all('p'):
                            maintext += i.text
                        article['maintext'] = maintext
                    except:
                        article['maintext'] = article['maintext'] 

                    print("newsplease maintext: ", article['maintext'][:50])

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
                        if colname !=  'articles-nodate':
                            url_count = url_count + 1
                        #print(article['date_publish'])
                        #print(article['date_publish'].month)
                        #print("+ TITLE: ",article['title'][0])
                        #print("+ MAIN TEXT: ",article['maintext'])
                        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        print("DUPLICATE! Not inserted.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
                processed_url_count += 1
                print('\n',processed_url_count, '/', len(list_urls), 'articles have been processed ...\n')

            else:
                pass


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")