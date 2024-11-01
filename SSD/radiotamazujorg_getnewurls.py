# Packages:
import sys
import os
import re
import getpass
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np 
from pymongo import MongoClient
import bs4
from bs4 import BeautifulSoup
from newspaper import Article
from dateparser.search import search_dates
import dateparser
import requests
import urllib.request
from warnings import warn
import json
from pymongo import MongoClient
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from pymongo.errors import CursorNotFound
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []


base = 'https://www.radiotamazuj.org/en/news/page/'
base = 'https://www.radiotamazuj.org/ar/blog/page/'
# base = 'https://www.radiotamazuj.org/en/category/opinions/page/'
opinion_scraping = False
for p in range(1, 60):
    sitemap = base + str(p) 
    print(sitemap)
    hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
    req = requests.get(sitemap, headers = hdr)
    soup = BeautifulSoup(req.content)
    item = soup.find_all('article')
    for i in item:
        url = i.find('h3', {'class' : 'article-title article-title-2'}).find('a')['href']
        direct_URLs.append(url)

    print(len(direct_URLs))

final_result = direct_URLs.copy()

url_count = 0
processed_url_count = 0
source = 'radiotamazuj.org'


for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            header = hdr = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=header)
            # process
            article = NewsPlease.from_html(response.text, url=url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            # title has no problem
            
            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser')
            
           
            try:
                title = soup.find('meta', {'property' : 'og:title'})['content']
                article['title'] = title
            except:
                title = soup.find("article", {'class' : 'article'}).find('h1').text
                article['title'] = title
            
            try:
                date = soup.find('meta', {'property' : 'article:published_time'})['content']
                article['date_publish'] = dateparser.parse(date)
            except:
                date = soup.find("span", {'class' : 'time'}).text.strip()
                article['date_publish'] = dateparser.parse(date)

            try:
                maintext = soup.find('div', {'class' : 'body-text'}).text
                article['maintext'] = maintext.strip()
            except:
                maintext = soup.find('meta', {'property' : 'og:description'})['content']
                article['maintext'] = maintext.strip()
                
            print("newsplease date: ",  article['date_publish'])
            print("newsplease title: ", article['title'])
            print("newsplease maintext: ", article['maintext'][:50])
        
            
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                if opinion_scraping:
                    colname = f'opinion-articles-{year}-{month}'
                    article['primary_location'] = "SSD"
                else:
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
