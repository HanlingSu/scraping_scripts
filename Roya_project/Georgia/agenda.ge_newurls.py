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

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p


direct_URLs = []
url_count = 0
processed_url_count = 0


source = 'agenda.ge'
for year in range(2020, 2024):
    for p in range(1, 5200):
        url = 'https://agenda.ge/en/news/' + str(year) + '/' + str(p)
        hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

        req = requests.get(url, headers = hdr)
        soup = BeautifulSoup(req.content)
        
        article = NewsPlease.from_html(req.text, url=url).__dict__      
        try:
            date = soup.find('div', {'class' : 'node-time text-blue'}).text.strip().split(',')[1]
            article['date_publish'] = dateparser.parse(date)
        except:
            article['date_publish'] = None
        print("newsplease date: ", article['date_publish'])
        print("newsplease title: ", article['title'])
        print("newsplease maintext: ", article['maintext'][:50])
        
        
        try:
            year = article['date_publish'].year
            month = article['date_publish'].month
            colname = f'articles-{year}-{month}'
            #print(article)
        except:
            colname = 'articles-nodate'
        #print("Collection: ", colname)
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
            print("ERRORRRR......", err, 'Inserted to error urls ....')
            
            pass
        processed_url_count += 1
        print('\n',processed_url_count,  'articles have been processed ...\n')
 
    else:
        pass


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
