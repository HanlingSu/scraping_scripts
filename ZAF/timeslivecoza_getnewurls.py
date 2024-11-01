from bs4 import BeautifulSoup, SoupStrainer
import requests
import re
from datetime import timedelta, date, datetime
from newspaper import Article
import newspaper
import pandas as pd
import time
import random
import dateparser
import os
import sys
from pandas.core.common import flatten
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from newsplease import NewsPlease
from dotenv import load_dotenv
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
import json
# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p



final_result = list(pd.read_csv('Downloads/peace-machine/peacemachine/getnewurls/ZAF/timeslive.csv')['0'])


source = 'timeslive.co.za'
url_count = 0
processed_url_count = 0

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
       

            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser')

            if not article['date_publish']:
                try:
                    date = json.loads(soup.find('script', {'type' : 'application/ld+json'}).contents[0])['datePublished']
                    article['date_publish'] = dateparser.parse(date).replace(tzinfo = None)
                except:
                    try:
                        date = soup.find('div', {'class' : 'article-pub-date'}).text.split('By')[0]
                        article['date_publish'] = dateparser.parse(date)
                    except:
                        article['date_publish'] = None
            print("newsplease date: ",  article['date_publish'])

            if not article['maintext']:
                try:
                    maintext = soup.find('div', {'class' : 'article-widgets'}).find('div', {'class' : 'text'}).text
                    article['maintext'] = maintext
                except:
                    soup.find('div', {'class' : 'article-wrapper--body'}).find_all('p')
                    maintext = ''
                    for i in soup.find('div', {'class' : 'article-wrapper--body'}).find_all('p'):
                        maintext += i.text
                    article['maintext'] = maintext.strip()
            print("newsplease maintext: ", article['maintext'][:50])

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
                myquery = { "url": url}
                db[colname].delete_one(myquery)
                # Inserting article into the db:
                db[colname].insert_one(article)
                print("DUPLICATE! Updated!")
                
                # pass
                # print("DUPLICATE! Not inserted.")

        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
