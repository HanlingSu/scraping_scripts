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

source = 'environnement.gov.mr'
direct_URLs = {}
base_url = 'http://www.environnement.gov.mr'


for p in range(3, 396, 3): 
    link = 'http://www.environnement.gov.mr/fr/index.php/toute-l-actualite?start=' + str(p) 
    print("Getting urls from: ", link)

    response = requests.get(link, verify=False)
    response.encoding = 'utf-8'

    soup = BeautifulSoup(response.content)
    
    # Get url and the date for each url 
    for article_header in soup.find_all('header'):
        title_tag = article_header.find('h2', {'class': 'uk-h1 title'})
        date_tag = article_header.find('p', {'class': 'meta'})

        if title_tag and title_tag.find('a') and date_tag and date_tag.find('time'):
            url = base_url + title_tag.find('a')['href']
            date_string = date_tag.find('time').get('datetime')
            parsed_date = dateparser.parse(date_string)
            direct_URLs[url] = parsed_date
        elif title_tag and title_tag.find('a'):
            url = base_url + title_tag.find('a')['href']
            direct_URLs[url] = None
            print(f"Warning: Date not found for URL on grid page: {url}")

    print('Now scraped ', len(direct_URLs), 'articles from previous months ... ')

print('There are ', len(direct_URLs), 'urls')
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
            soup = BeautifulSoup(response.content)
            article = NewsPlease.from_html(response.text, url=url).__dict__

            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            article['url'] = url
            article['environmental'] = True

            # Extract text 
            try: 
                maintext = soup.find('div', {'itemprop': 'articleBody'}).text
                article['maintext'] = maintext.strip()
            except: 
                maintext = "" 
                for i in soup.find('div', {'itemprop': 'articleBody'}).find_all('div', {'class': 'x11i5rnm xat24cr x1mh8g0r x1vvkbs xtlvy1s x126k92a'}):
                    if i:
                        maintext += i.text
                article['maintext'] = maintext.strip()

            # Extract date 
            article['date_publish'] = direct_URLs.get(url)
            print("Extracted date from grid: ", article['date_publish'])

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
