# Packages:
from pymongo import MongoClient
import re
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
from newsplease import NewsPlease
from dotenv import load_dotenv
import cloudscraper 
from urllib.parse import urljoin

hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'eco.gov.uz'
direct_URLs = set()
base_url = 'https://eco.gov.uz'
languages = ['en', 'ru', 'yz', 'uz']
pages = () 

for p in range(1, 459):
    link = 'https://eco.gov.uz/en/posts?categoryId=6&page=' + str(p) + '&per-page=6'
    print("Getting urls from: ",link)
    response = requests.get(link, verify=False)
    response.encoding = 'utf-8'

    soup = BeautifulSoup(response.content)
    for i in soup.find_all('div', {'class' : 'news_img_title'}):
        relative_url = i.find('a')['href']
        full_url = urljoin(base_url, relative_url)
        
        # Add the full URL to the set
        direct_URLs.add(full_url)
    print('Now scraped ', len(direct_URLs), 'articles from previous months ... ')

final_result = list(direct_URLs).copy()

print('The total count of final result is: ', len(final_result))

url_count = 0
processed_url_count = 0
for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            # process
            response = requests.get(url, verify=False)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')
            article = NewsPlease.from_html(response.text, url=url).__dict__

            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            article['url'] = url
            article['environmental'] = True
            
            # Extract text
            try:
                maintext = soup.find('div', {'class': 'learn_more_news_single_text img_width'}).text
                article['maintext'] = maintext.strip()
            except:
                maintext = ""
                for i in soup.find('div', {'class': 'learn_more_news_single_text img_width'}).find_all('p'):
                    if i:
                        maintext += i.text
                article['maintext'] = maintext.strip()

            # Extract title
            try:
                title = soup.find('div', {'class': 'news_single_title'}).text
                article['title'] = title.strip()
            except:
                article['title'] = article.get('title', 'No Title Found') 

            # Extract date
            try: 
                date = soup.find('div', {'class': 'date'}).text.strip()
                lines = [ln.strip() for ln in date.splitlines() if ln.strip()]
                lines = [ln for ln in lines if not re.fullmatch(r'\d+', ln)]
                day = lines[0].rstrip('.')  
                month = lines[1].replace('.', '')    
                hour  = lines[2]
  
                clean = f"{day} {month} {hour}"
                article_date = dateparser.parse(clean, settings={'DATE_ORDER':'DMY'})
                article['date_publish'] = article_date  
            except:
                article['date_publish'] = None

            print("newsplease date: ", article['date_publish'])
            print("newsplease title: ", article['title'])
            print("newsplease maintext: ", article['maintext'][:150])
            
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
                # myquery = { "url": final_url, "source_domain" : 'web.archive.org'}
                # db[colname].delete_one(myquery)
                # Inserting article into the db:
                db[colname].insert_one(article)
                # count:
                url_count = url_count + 1
                print("Inserted! in ", colname, " - number of urls so far: ", url_count)
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
