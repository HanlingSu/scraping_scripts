# Packages:
from pymongo import MongoClient
import re
import bs4
from bs4 import BeautifulSoup
from newspaper import Article
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

source = 'kilimokwanza.org'
direct_URLs = set()

for year in range(2003, 2026):
    for month in range(1, 13):
        month_str = f"{month:02d}"

        # Page 1 (root URL for month)
        root_url = f"https://kilimokwanza.org/{year}/{month_str}/"
        print(f"Scraping (detect max page): {root_url}")
        try:
            response = requests.get(root_url, headers=hdr)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Detect max page
            pagination = soup.select('nav.pagination .page-numbers')
            page_numbers = [int(link.text) for link in pagination if link.text.isdigit()]
            max_page = max(page_numbers) if page_numbers else 1
            print(f"Detected max page: {max_page}")

            # Always start with root_url (page 1)
            pages = [root_url] + [
                f"https://kilimokwanza.org/{year}/{month_str}/page/{p}/" for p in range(2, max_page + 1)
            ]

            for url in pages:
                print(f"Scraping: {url}")
                try:
                    response = requests.get(url, headers=hdr)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    articles = soup.find_all('h2', {'class': 'title'})

                    for article in articles:
                        a_tag = article.find('a')
                        if a_tag and a_tag.get('href'):
                            article_url = a_tag['href']
                            direct_URLs.add(article_url)
                except Exception as e:
                    print(f"Failed to scrape: {url} — {e}")
                    continue

        except Exception as e:
            continue
        
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

            # Extract maintext 
            try: 
                maintext = soup.find('div', {'class': 'post-single-content box mark-links'}).text
                article['maintext'] = maintext.strip()
            except: 
                maintext = ""
                for i in soup.find('div', {'class': 'post-single-content box mark-links'}).find_all('p'):
                    maintext += i.text
                    article['maintext'] = maintext.strip()

        
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
