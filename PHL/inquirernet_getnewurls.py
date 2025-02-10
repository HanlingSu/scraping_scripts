# Packages:
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

direct_URLs = []
base = 'https://newsinfo.inquirer.net/category/latest-stories/page/'

# opinion_base = "https://opinion.inquirer.net/category/editorial/page/"
for i in range(1, 390):
    link = base + str(i) 
    hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
    req = requests.get(link, headers = hdr)
    soup = BeautifulSoup(req.content)
    item = soup.find_all('div', {'id' : 'ch-ls-box'})
    for i in item:
        try:
            url = i.find('a')['href']
            direct_URLs.append(url)
        except:
            pass

    print(len(direct_URLs))
final_result = direct_URLs.copy()
print(len(final_result))

url_count = 0
processed_url_count = 0
source = 'inquirer.net'
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
            print("newsplease title: ", article['title'])
#             print("newsplease maintext: ", article['maintext'])
            print("newsplease date: ",  article['date_publish'])
            
            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser')
            
            try:
                soup.find('div', {'id':'article_content'}).find_all('p')
                maintext = ''
                for i in soup.find('div', {'id':'article_content'}).find_all('p'):
                    if 'ADVERTISEMENT' not in i.text.strip():
                        maintext += i.text.strip()
                article['maintext'] = maintext
            except: 
                try: 
                    for i in soup.find('div', {'id':'article_content'}).find_all('div', {'class':'a3s'}):
                        maintext += i.text.strip()
                        article['maintext'] = maintext
                except:
                    try:
                        for i in soup.find('div', {'id':'article-content'}).find_all('p'):
                            maintext += i.text.strip()
                            article['maintext'] = maintext
                        print('second try')

                    except:
                        try:
                            maintext = soup.find('meta',  property="og:description" )['content']
                            article['maintext'] = maintext.strip()
                            print('thrid try')

                        except:  
                            try:
                                for i in soup.find('div', {'id':'article-content'}).find_all('div', {'class':'a3s'}):
                                    maintext += i.text.strip()
                                    article['maintext'] = maintext   
                                print('fourth try')
                            except:
                                try:
                                    for i in soup.find_all('p'):
                                        maintext += i.text.strip()
                                        article['maintext'] = maintext
                                    print('fifth try')

                                except:
                                    article['maintext']  = None
                                    print('Empty maintext!')

            if article['maintext']:
                print(article['maintext'][:50])

            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                if "/opinion" in url:
                    colname = f'opinion-articles-{year}-{month}'
                    article['primary_location'] = "PHL"
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
