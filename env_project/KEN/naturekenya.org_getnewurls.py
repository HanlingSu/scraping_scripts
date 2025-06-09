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
from dateutil import parser as dateparser

hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'naturekenya.org'
base = "https://newslinekg.com"
url_count = 0
processed_url_count = 0
len_final_result = 0

direct_URLs = set()

base = "https://naturekenya.org"
source = "naturekenya.org"

for year in range(2016, 2026):  
    year_str = str(year)
    for month in range(12, 13):  
        month_str = str(month).zfill(2)

        # Do not include day, just year and month
        link = f"{base}/{year_str}/{month_str}/"
        print("Scraping:", link)

        direct_URLs = []
        try:
            response = requests.get(link, headers=hdr, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            for i in soup.find_all('h2', {'class': 'entry-title'}):
                a_tag = i.find('a')
                if a_tag and 'href' in a_tag.attrs:
                    href = a_tag['href']
                    if not href.startswith('http'):
                        href = base + href
                    direct_URLs.append(href)
        except Exception as e:
            print("Request error on page:", link, "-", e)

        final_result = direct_URLs
        print(final_result)
        len_final_result += len(final_result)

        for url in final_result:
            if url:
                print(url, "FINE")
                try:
                    article_response = requests.get(url, headers=hdr, timeout=10)
                    article = NewsPlease.from_html(article_response.text, url=url).__dict__

                    article['date_download'] = datetime.now()
                    article['download_via'] = "Direct2"
                    article['source_domain'] = source
                    article['url'] = url
                    article['environmental'] = True

                    # Extract date
                    try:
                        date = soup.find('time', {'class':'entry-date published updated'}).text.strip()
                        print(date)
                        article['date_publish'] = dateparser.parse(date)
                    except:
                        article['date_publish'] = None

                    print("newsplease date:", article['date_publish'])
                    print("newsplease title:", article['title'])
                    print("newsplease maintext:", article['maintext'][:50])

                    try:
                        year = article['date_publish'].year
                        month = article['date_publish'].month
                        colname = f'articles-{year}-{month}'
                    except:
                        colname = 'articles-nodate'

                    try:
                        db[colname].insert_one(article)
                        url_count += 1
                        print("Inserted into", colname, "- total:", url_count)
                        db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        print("DUPLICATE! Not inserted.")
                except Exception as err:
                    print("ERROR scraping article:", err)
                processed_url_count += 1
                print(f'\n{processed_url_count}/{len_final_result} articles processed...\n')

print("Done inserting", url_count, "manually collected URLs from", source, "into the DB.")