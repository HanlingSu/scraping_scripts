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

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)

hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'baq.kz'
direct_URLs = set()

for p in range(1, 4):
    link = link = 'https://baq.kz/tag/qorshagan-orta/?page=' + str(p)
    print("Getting urls from: ", link)
    soup = BeautifulSoup(scraper.get(link).text)

    # Select the articles grid
    article_links = soup.find_all('a', {'class': 'item-list__link'})
    print(f"Found {len(article_links)} articles on page {p}")

    for link_tag in article_links:
        url = link_tag['href']
        # Find the title tag to each link 
        title_span = link_tag.find('span', {'class': 'item-list__title'})

        if title_span:
            title = title_span.get_text(strip=True)
            direct_URLs.add((url, title))
            # print(f"Added: {title[:30]}... - {url}")
        else:
            print(f"Found link but no title: {url}")  
    
                        
    print('Now scraped ', len(direct_URLs), 'articles from previous months ... ')
print('There are ', len(direct_URLs), 'urls')

final_result = list(direct_URLs).copy()

print('The total count of final result is: ', len(final_result))

url_count = 0
processed_url_count = 0

for url_title_tuple in final_result:
    url = url_title_tuple[0]  # Extract just the URL string
    title = url_title_tuple[1]  # Extract just the title
    
    print(url, "FINE")
    
    try:
        # Process article with NewsPlease
        soup = BeautifulSoup(scraper.get(url).text)
        article = NewsPlease.from_html(scraper.get(url).text).__dict__
        article['date_download'] = datetime.now()
        article['download_via'] = "Direct2"
        article['source_domain'] = source
        article['url'] = url  # Ensure URL is stored correctly
        article['environmental'] = True

        # Extract text
        try:
            maintext = ""
            container = soup.find('div', {'class': 'news-text'})
            if container:
                for element in container.find_all(['p', 'h4']):
                    maintext += element.get_text(" ", strip=True) + " "
            article['maintext'] = maintext.strip()
        except:
            article['maintext'] = ""
        
        print("newsplease date: ", article['date_publish'])
        print("newsplease title: ", article['title'])
        print("newsplease maintext: ", article['maintext'][:200])
        
        try:
            year = article['date_publish'].year
            month = article['date_publish'].month
            colname = f'articles-{year}-{month}'
        except:
            colname = 'articles-nodate'
        
        try:
            # Inserting article into the db:
            db[colname].insert_one(article)
            
            # Count successful inserts
            url_count = url_count + 1
            print("Inserted! in ", colname, " - number of urls so far: ", url_count)
            
            # Add to URLs collection
            db['urls'].insert_one({'url': article['url']})
            
        except DuplicateKeyError:
            print("DUPLICATE! Not inserted.")
        except Exception as err:
            print("ERRORRRR......", err)
            pass
            
        processed_url_count += 1
        print('\n', processed_url_count, '/', len(final_result), 'articles have been processed ...\n')
        
    except Exception as e:
        print(f"Error processing article: {e}")
        processed_url_count += 1
        print('\n', processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

print("Done inserting ", url_count, " manually collected urls from ", source, " into the db.")