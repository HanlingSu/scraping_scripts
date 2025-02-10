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
import re
import pandas as pd

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'makfax.com.mk'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}


base = 'https://makfax.com.mk/sitemap-pt-post-p'

direct_URLs = []
for year in range(2024, 2025):
    for month in range(9, 12):
        monthly_URLs = []
        year_str = str(year)
        if month <10:
            month_str = '0' + str(month)
        else:
            month_str = str(month)
        print('Now scraping', year_str, month_str)
        
        for p in range(1, 350):
            sitemap = base +str(p) + '-' + year_str +'-' + month_str + '.html'
            # print(sitemap)
            req = requests.get(sitemap, headers = headers)
            soup = BeautifulSoup(req.content)
            if  len(soup.find_all('td'))>0 :
                for i in soup.find_all('td'):
                    try:
                        monthly_URLs.append(i.find('a')['href'])
                    except:
                        pass
            else:
                break
                
        print('Now collected', len(monthly_URLs), 'URLs from current month ... ')
        
        direct_URLs.extend(list(set(monthly_URLs)))
    direct_URLs = list(set(direct_URLs))
    print('...... Now collected', len(direct_URLs), 'URLs from', year_str,  ' ......')
        
blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

final_result = list(set(direct_URLs))


print("Total number of urls found: ", len(final_result))

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

            
            print("newsplease title: ", article['title'])
            print("newsplease date: ", article['date_publish'])
            soup = BeautifulSoup(response.text, 'html.parser')

            try:
                maintext = ''
                for i in soup.find('div', {'id' : 'mvp-content-main'}).find_all('p'):
                    maintext += i.text
                article['maintext'] = maintext
            except:
                article['maintext'] = soup.find('div', {'id' : 'mvp-content-main'}).text.replace('\n', '').strip()
            
            if  article['maintext']:
                print("newsplease maintext: ", article['maintext'][:50])
            
              
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
