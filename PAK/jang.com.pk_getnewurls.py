#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sep 11 2023

@author: Hanling
 
"""
# Packages:
import sys
sys.path.append('../')
from pymongo import MongoClient
from urllib.parse import urlparse
from datetime import datetime
from pymongo.errors import DuplicateKeyError
import requests
from newsplease import NewsPlease
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import dateparser
import json


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## NEED TO DEFINE SOURCE!
source = 'jang.com.pk'

base = "https://jang.com.pk/news/"
# daily sitemap
# https://jang.com.pk/assets/uploads/google_news_latest.xml

direct_URLs = []
# 660000
for i in range(1357979,1390235):
    direct_URLs.append(base + str(i))


final_result = direct_URLs.copy()
## INSERTING IN THE DB:
url_count = 0
processed_url_count = 0

for url in final_result:
    try:
        print(url)
        #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
        header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        response = requests.get(url, headers=header)
        # process
        article = NewsPlease.from_html(response.text, url=url).__dict__
        # add on some extras
        article['date_download']=datetime.now()
        article['download_via'] = "Direct2"
        article['language'] = "ur"
        
        ## Fixing Date:
        soup = BeautifulSoup(response.text, 'html.parser')

        if article['title']:
            print('newsplease title', article['title'])

        # Get Main Text:
        try:
            if soup.find('div', {'class' : 'detail_view_content'}).find_all('p'):
                maintext = ''
                for i in soup.find('div', {'class' : 'detail_view_content'}).find_all('p'):
                    maintext += i.text
                article['maintext'] = maintext.strip()
            if not article['maintext']:
                maintext = soup.find('div', {'class' : 'detail_view_content'}).text
                article['maintext'] = maintext.strip()
        except: 
            article['maintext'] = article['maintext'].strip()
        if article['maintext']:
            print('newsplease maintext', article['maintext'][:50])

        # Get Date
        if not article['date_publish']:
            try:
                date = json.loads(soup.find('script', {'type' : 'application/ld+json'}).contents[0], strict=False)['datePublished']
                article['date_publish'] = dateparser.parse(date).replace(tzinfo=None)
            except:
                article['date_publish'] =  article['date_publish']  
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
            # myquery = { "url": url}
            # db[colname].delete_one(myquery)
            # Inserting article into the db:
            # db[colname].insert_one(article)
            # print("DUPLICATE! UPDATED.")
            print("DUPLICATE! Not inserted.")
    except Exception as err: 

        print("ERRORRRR......", err)
        pass
    processed_url_count += 1
    print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db." )