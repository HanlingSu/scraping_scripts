#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Apr 2 2021

@author: diegoromero

This script updates nuevaya.com.ni using section sitemaps.
You can run this script as often as you want.
 
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

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


## COLLECTING URLS
urls = []

## NEED TO DEFINE SOURCE!
source = 'nuevaya.com.ni'

# Custom Parser:
def nuevayacomni_story(soup):
    """
    Function to pull the information we want from nuevaya.com.ni stories
    :param soup: BeautifulSoup object, ready to parse
    """
    # create a dictionary to hold everything in
    hold_dict = {}
    
    # Get Title: 
    try:
        article_title = soup.find("title").text
        hold_dict['title']  = article_title   

    except:
        hold_dict['title']  = None
        
    # Get Main Text:
    try:
        #maintext = soup.find('p', attrs={'class':'entry-excerpt entry-excerpt-content-custom'}).text
        contains_text = soup.findAll('p')
        if len(contains_text) > 1:
          if len(contains_text) == 2:
            maintext = contains_text[0].text + contains_text[1].text
          else:
            maintext = contains_text[0].text + contains_text[1].text + contains_text[2].text
        else:
          maintext = contains_text[0].text
        if "Publicado el" in maintext:
          maintext = maintext[12:]
        hold_dict['maintext'] = maintext
    except: 
        hold_dict['maintext']  = None

    # Get Date:
    #meta property="article:published_time" content="2022-04-02T16:26:32+00:00"
    try:
        contains_date = soup.find("meta", {"property": "article:published_time"})
        article_date = dateparser.parse(contains_date['content'])
        hold_dict['date_publish'] = article_date  

    except:
        article_date = None
        hold_dict['date_publish'] = None  

    return hold_dict 

# STEP 0: Get sitemap urls:
# post-sitemap 
#for j in range(1,3):
# for j in range(1,489):
#     url = 'https://nuevaya.com.ni/post-sitemap' + str(j) + '.xml'

#     print("Sitemap: ", url)

#     reqs = requests.get(url, headers=headers)
#     soup = BeautifulSoup(reqs.text, 'html.parser')

#     for link in soup.findAll('loc'):
#         urls.append(link.text)

#     print("URLs so far: ", len(urls))


# Step 1: URLs from the "todas-nuestras-noticias" section
#for i in range(8560,8562):
for i in range(1, 300):
    if i == 1:
        url = 'https://nuevaya.com.ni/todas-nuestras-noticias/'
    else:
        url = 'https://nuevaya.com.ni/todas-nuestras-noticias/page/' + str(i) + '/'

    print("URL: ", url)

    reqs = requests.get(url, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    for link in soup.find_all('h3',{ 'class' : 'entry-title td-module-title'}):
            urls.append(link.find('a')['href']) 
    
    print("URLs so far: ", len(urls))

# KEEP ONLY unique URLS:
dedupurls = list(set(urls))

#dftest = pd.DataFrame(urls)  
#dftest.to_csv('/Users/diegoromero/Downloads/test.csv')  

# STEP 3: Get rid or urls from blacklisted sources
blpatterns = ['deportes-ya/', '/deportes/']

list_urls = []
for url in dedupurls:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            print(url)
            if "nuevaya.com.ni" in url:
                count_patterns = 0
                for pattern in blpatterns:
                    if pattern in url:
                        count_patterns = count_patterns + 1
                if count_patterns == 0:
                    list_urls.append(url)

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
            if 'nuevaya.com.ni' in url:
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
                    article['source_domain'] = 'nuevaya.com.ni'
                    
                     ## Fixing what needs to be fixed:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    if soup.find('a',{ "title" : 'Ver todas las publicaciones en Deportes YA'}):
                        article['title'] = 'From uninterested category'
                        article['maintext'] = None
                        article['date_publish'] = None
                        print(article['title'], soup.find('a',{ "title" : 'Ver todas las publicaciones en Deportes YA'}).text)
                    else:
                        # TITLE:
                        if article['title'] == None:
                            try:
                                article['title'] = nuevayacomni_story(soup)['title']
                            except:
                                article['title'] == None
                        print('newsplease title', article['title'])

                        # MAIN TEXT:
                        if article['maintext'] == None:
                            try:
                                article['maintext'] = nuevayacomni_story(soup)['maintext']
                            except:
                                article['maintext'] == None
                        if  article['maintext']:
                            print('newsplease maintext', article['maintext'][:50])

                        # Fixing date:
                        if article['date_publish'] == None:
                            try:
                                article['date_publish'] = nuevayacomni_story(soup)['date_publish']
                            except:
                                article['date_publish'] == None
                        print('newsplease date', article['date_publish'])
                    

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
                        if colname != 'articles-nodate':
                            url_count = url_count + 1
                            print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        else:
                            print("Inserted! in ", colname)
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