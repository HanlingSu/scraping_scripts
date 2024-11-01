from pymongo import MongoClient
import bs4
from bs4 import BeautifulSoup
from newspaper import Article
from dateparser.search import search_dates
import dateparser
import requests
from urllib.parse import quote_plus
import pandas as pd
from random import randint, randrange
from warnings import warn
import json
from pymongo import MongoClient
from urllib.parse import urlparse
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
from dotenv import load_dotenv

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []

# Adjust the base URL and the range of sitemaps to iterate over (133 to 135 inclusive)
base = "https://cnnespanol.cnn.com/post-sitemap"
for p in range(133, 136):  # range includes 135
    link = base + str(p) + '.xml'
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = requests.get(link, headers=hdr)
    soup = BeautifulSoup(req.content, 'xml')  # use 'xml' parser for better handling of sitemap XML
    for i in soup.find_all('loc'):
        direct_URLs.append(i.text)
    print("Now collected ", len(direct_URLs), "articles ... ")

direct_URLs = list(set(direct_URLs))

final_result = direct_URLs.copy()
print(len(final_result))
print(final_result[:5])

url_count = 0
processed_url_count = 0
source = 'cnnespanol.cnn.com'

for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            response = requests.get(url, headers=header)
            
            # Scraping article
            article = NewsPlease.from_html(response.text, url=url).__dict__
            article['date_download'] = datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source

            # Filter for articles published in September 2024
            if article['date_publish']:
                publish_date = article['date_publish']
                if publish_date.year == 2024 and publish_date.month == 9:
                    print('Date confirmed: ', article['date_publish'])
                    
                    if article['title']:
                        print('Title confirmed: ', article['title'])
                    if article['maintext']:
                        print('Main text preview:', article['maintext'][:50])

                    # Collection name based on year and month
                    year = publish_date.year
                    month = publish_date.month
                    colname = f'articles-{year}-{month}'

                    try:
                        # Insert into the correct MongoDB collection
                        db[colname].insert_one(article)
                        url_count += 1
                        print("Inserted! in ", colname, " - number of URLs so far: ", url_count)
                        db['urls'].insert_one({'url': article['url']})

                    except DuplicateKeyError:
                        print("DUPLICATE! Not inserted.")
                else:
                    print(f"Article is not from September 2024, skipping: {publish_date}")
            else:
                print("No publish date found, skipping.")
        except Exception as err:
            print("ERROR......", err)
            pass
        
        processed_url_count += 1
        print('\n', processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

print("Done inserting ", url_count, " manually collected URLs from ", source, " into the db.")
