from pymongo import MongoClient
import bs4
from bs4 import BeautifulSoup
from newspaper import Article
from dateparser.search import search_dates
import dateparser
import requests
from urllib.parse import quote_plus
from random import randint, randrange
from warnings import warn
import json
from urllib.parse import urlparse
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
from dotenv import load_dotenv
import re

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []

base = "https://asia.nikkei.com/search?contentType=article&facet%5B0%5D=article_display_date_value_dt%3A%221month%22&query=is&sortBy=newest&dateFrom=01-09-2024&dateTo=15-10-2024&page="

for p in range(1, 24):
    link = base + str(p)
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = requests.get(link, headers=hdr)
    soup = BeautifulSoup(req.content)
    for h2 in soup.find_all('h2', {'class': 'ArticleSearchResult_headline__y2pzy'}):
        direct_URLs.append(h2.find('a')['href'])
    print("Now collected ", len(direct_URLs), "articles ... ")

# Remove duplicates
direct_URLs = list(set(direct_URLs))

# Define `source` before using it in the MongoDB query
source = 'asia.nikkei.com'

# Fetch blacklist URL patterns from MongoDB based on `source`
blacklist = [(i['blacklist_url_patterns']) for i in db.sources.find({'source_domain': source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))

# Filter URLs that are not blacklisted
direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

final_result = ['https://asia.nikkei.com' + i for i in direct_URLs]
print(len(final_result))
print(final_result[:5])

url_count = 0
processed_url_count = 0

for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            response = requests.get(url, headers=header)
            
            article = NewsPlease.from_html(response.text, url=url).__dict__
            article['date_download'] = datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source

            if article['date_publish']:
                print('Date modified! ', article['date_publish'])
                
            if article['title']:
                print('Title modified! ', article['title'])
                
            if article['maintext']:
                print('Maintext modified!', article['maintext'][:50])

            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'articles-{year}-{month}'
            except:
                colname = 'articles-nodate'

            try:
                db[colname].insert_one(article)
                if colname != 'articles-nodate':
                    url_count += 1
                    print(f"Inserted in {colname} - number of URLs so far: {url_count}")
                else:
                    print(f"Inserted in {colname}")
                db['urls'].insert_one({'url': article['url']})
            except DuplicateKeyError:
                print("DUPLICATE! Not inserted.")
        except Exception as err:
            print("ERRORRRR......", err)
            pass

        processed_url_count += 1
        print(f'\n{processed_url_count} / {len(final_result)} articles have been processed ...\n')

print(f"Done inserting {url_count} manually collected URLs from {source} into the DB.")
