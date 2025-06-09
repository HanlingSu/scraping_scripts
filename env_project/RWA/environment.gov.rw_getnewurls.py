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


hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'environment.gov.rw'
direct_URLs = set()
base = 'https://www.environment.gov.rw'

initial_url = f'{base}/news/page?tx_news_pi1%5BcurrentPage%5D=1'
print("Getting cHash from:", initial_url)

response = requests.get(initial_url, verify=False)
soup = BeautifulSoup(response.content, 'html.parser')

# Get the hash 
cHash = None
for link in soup.find_all('a', href=True):
    if 'tx_news_pi1%5BcHash%5D' in link['href']:

        cHash = link['href'].split('cHash=')[1].split('&')[0]
        break

if not cHash:
    print("cHash not found on the first page.")
else:
    print("Found cHash:", cHash)

for p in range(1, 17):
    link = f'{base}/news/page?tx_news_pi1%5BcurrentPage%5D={p}&cHash={cHash}'
    print("Getting urls from: ", link)

    response = requests.get(link, verify=False)
    soup = BeautifulSoup(response.content)
    

    for i in soup.find_all('div', {'class': 'articletype-0'}):

        a_tag = i.find('a', href=True, title=True)
        if a_tag and a_tag.get('href'):
            href = a_tag.get('href')
            url = base + href

            date_tag = i.find('time', {'itemprop': 'datePublished'})
            if date_tag and date_tag.get('datetime'):
                article_date = date_tag['datetime']
            else:
                article_date = None

            direct_URLs.add((url, article_date))

    print('Now scraped ', len(direct_URLs), 'articles from previous months ... ')


print('There are ', len(direct_URLs), 'urls')
final_result = list(direct_URLs).copy()

print('The total count of final result is: ', len(final_result))

url_count = 0
processed_url_count = 0
for url, article_date in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            # process
            response = requests.get(url, verify=False)
            soup = BeautifulSoup(response.content)
            article = NewsPlease.from_html(response.text, url=url).__dict__

            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            article['url'] = url
            article['environmental'] = True
            
            if article_date:
                article['date_publish'] = dateparser.parse(article_date)
            else:
                # Try to extract date from the article's own page if not found on the main page
                try:
                    date_tag = soup.find('time', {'itemprop': 'datePublished'})
                    if date_tag and date_tag.get('datetime'):
                        article['date_publish'] = dateparser.parse(date_tag['datetime'])
                    else:
                        article['date_publish'] = None  # Handle missing date
                except Exception as e:
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

