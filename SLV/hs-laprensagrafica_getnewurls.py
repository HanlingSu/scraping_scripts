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
import time
import cloudscraper

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)



direct_URLs = pd.read_csv('Downloads/peace-machine/peacemachine/getnewurls/SLV/laprensagrafica_opinion.csv')['0']


source = 'laprensagrafica.com'


blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]


final_result = direct_URLs.copy()[::-1]

url_count = 0
processed_url_count = 0


for url in final_result:
    if url:
        print(url, "FINE")
        time.sleep(6)
        ## SCRAPING USING NEWSPLEASE:
        try:
            header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            # process
            article = NewsPlease.from_html(scraper.get(url).text).__dict__

            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            # title has no problem
            
            # custom parser
            soup = BeautifulSoup(scraper.get(url).text)
            try:
                date = json.loads(soup.find_all('script', {'type' : "application/ld+json"})[1].contents[0], strict=False)['datePublished']
                article['date_publish'] = dateparser.parse(date)
            except:
                date = soup.find('time')['datetime']
                article['date_publish'] = dateparser.parse(date)

            print("newsplease date: ",  article['date_publish'])
            print("newsplease title: ", article['title'])
            print("newsplease maintext: ", article['maintext'][:50])

            if '/opinion/' in url or '/editorial/' in url:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'opinion-articles-{year}-{month}'
                article['primary_location'] = "SLV"
            else:
            
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
                # db['urls'].insert_one({'url': article['url']})
            except DuplicateKeyError:
                # db[colname].delete_one({'ulr' : url})
                # db[colname].insert_one(article)
                pass
                print("DUPLICATE! Pass.")
                
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')
 
    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
