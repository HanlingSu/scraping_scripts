# Packages:
from builtins import len
import sys
import os
import re
import getpass
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np 
from tqdm import tqdm

from pymongo import MongoClient


import bs4
from bs4 import BeautifulSoup
from newspaper import Article
from dateparser.search import search_dates
import dateparser
import requests
from urllib.parse import quote_plus

import urllib.request
import time
from time import time
import random
from random import randint, randrange
from warnings import warn
import json
from pymongo import MongoClient
from urllib.parse import urlparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from pymongo.errors import CursorNotFound
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from dotenv import load_dotenv

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


source = 'elnorte.ec'
# base_list = ['https://www.elnorte.ec/post-sitemap1.xml', 'https://www.elnorte.ec/post-sitemap2.xml']
direct_URLs = []

# collect new URLs from sitemaps
# for base in base_list:
#     reqs = requests.get(base, headers=headers)
#     soup = BeautifulSoup(reqs.text, 'html.parser')

#     for link in soup.find_all('loc'):
#         direct_URLs.append(link.text)

#     print(len(direct_URLs))

# collect new URLs from categorized news
categories = ['tag/bicentenario', 'ciudad', 'tendencia', 'tag/elecciones']
page_start = [1, 1, 1, 1]
page_end = [10, 10, 10, 5]
# page_end = [10, 5, 1]

for c, ps, pe in zip(categories, page_start, page_end):
    for i in range(ps, pe+1):
        link = 'https://www.elnorte.ec/'+c+'/page/'+str(i)
        reqs = requests.get(link, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        for link in soup.find_all('h3', {'class' : 'elementor-post__title'}):
            direct_URLs.append(link.find('a')['href'])

        print('Now scraped', len(direct_URLs), 'from previous pages ...')




print(direct_URLs[:5])
direct_URLs =list(set(direct_URLs))

print(len(direct_URLs))
final_result = direct_URLs

url_count = 0
processed_url_count =0
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
            #print("newsplease date: ", article['date_publish'])
#             print("newsplease maintext: ", article['maintext'][:50])

           
            soup = BeautifulSoup(response.content, 'html.parser')
            try:
                category = soup.find('meta', property = 'article:section')['content']
                # print(category)
            except:
                category = 'news'

            if category in ['Deportes', 'Home Izquierda 1', 'Tecnología']:
                article['title'] = 'From uninterested category'
                print(article['title'])
                article['maintext'] = None
                article['date_publish'] = None
            else:
                # Get Title: 
                try:
                    article_title = soup.find('meta', {"name" : "og:title"})['content'].split('-')[0]
                    article['title']  = article_title   
                except:
                    try:
                        article_title = soup.find('title').text.split('-')[0]
                        article['title']  = article_title  
                    except:
                        try:
                            article_title = soup.find('h3').text.split('\n')[1].strip(' ')
                            article['title']  = article_title  
                        except:
                            pass
                if article['title']:
                    print('Title modified: ', article['title'] )    

                # Get Main Text:
                try:
                    soup.find('div', {'class': 'entry-content'}).find_all('p')
                    maintext = ''
                    for i in soup.find('div', {'class': 'entry-content'}).find_all('p'):
                        maintext += i.text
                    article['maintext'] = maintext
                except: 
                    maintext = article['maintext']
                    article['maintext'] = maintext
                if article['maintext']:
                    print('Maintext modified: ', article['maintext'][:50] )    
  
      
                # Get Date
                try:
                    date = soup.find('time')['datetime']
                    article['date_publish'] = dateparser.parse(date)

                except:
                    try:
                        date = json.loads(soup.find('script', type='application/ld+json').string)['@graph'][4]['datePublished'].split('T')[0]
                        article['date_publish'] = dateparser.parse(date)
                    except:
                        pass
                if article['date_publish']:
                    print('Date modified: ', article['date_publish'])    
  
            # print('Manually scraped date is ', article['date_publish'])

        

            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'articles-{year}-{month}'
                #print(article)
            except:
                colname = 'articles-nodate'
            #print("Collection: ", colname)
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
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")

