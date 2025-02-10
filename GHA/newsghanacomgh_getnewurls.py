#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on feb 2 2022

@author: hanling

This script updates newsghana.com.gh -- it must be edited to 
scrape the most recent articles published by the source.

It needs to be run everytime we need to update GHA sources. 
"""
# Packages:
from pymongo import MongoClient
from bs4 import BeautifulSoup
from dateparser.search import search_dates
import dateparser
import requests
from urllib.parse import quote_plus
import time
from datetime import datetime
from pymongo.errors import DuplicateKeyError
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from dotenv import load_dotenv


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

direct_URLs = []

###################################
# edit sitemap ending number here #
###################################``

base = 'https://newsghana.com.gh'

categories = ['/world-news/', '/ghana-news/', '/headlines/']
page_start = [1, 1, 1]
page_end = [90, 450, 100]
for c, ps, pe in zip(categories, page_start, page_end):
    for p in range(ps, pe+1):
        url = base + c + 'page/' + str(p) 
        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')
        # print('Now scraping ', url)
        for i in soup.find_all('h3', {'class' : 'entry-title td-module-title'}):
            direct_URLs.append(i.find('a')['href'])
        print(len(direct_URLs))

final_result = list(set(direct_URLs))

print("Total number of urls found: ", len(final_result))

# insert news articles
url_count = 0
processed_url_count = 0
source = 'newsghana.com.gh'
for url in final_result:
    if url:
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
            article['source_domain'] = source
            # title has no problem
            print("newsplease title: ", article['title'])
            print("newsplease maintext: ", article['maintext'][:50])
            print("newsplease date: ",  article['date_publish'])
            
            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser')
            
            try:
                category = soup.find('meta',  property =  'article:section')['content']
            except:
                category = 'News'
            
            if category in  ['Sports', 'Entertainment', 'Business', 'Travel', 'Science', 'Rumor Mill',\
                     'Opinion', 'Auto', 'Real Estates', 'BusinessWire', 'Finance', 'Agriculture', 'Investments', \
                         'Stock Market', 'Environmental news', 'Technology', 'Lifestyle', 'Profile']: 
                article['title'] = 'From uninterested category'
                article['date_publish'] = None
                article['maintext'] = None
                print(article['title'], category)
                
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'articles-{year}-{month}'
                
            except:
                colname = 'articles-nodate'
            
            # Inserting article into the db:
            try:
                db[colname].insert_one(article)
                # count:
                if colname != 'articles-nodate':
                    url_count = url_count + 1
                    print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                db['urls'].insert_one({'url': article['url']})
            except DuplicateKeyError:
                pass
                print("DUPLICATE! Not inserted.")
                
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')
 
    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
