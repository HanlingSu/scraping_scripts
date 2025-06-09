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

source = 'albiaanews.com.tn'
direct_URLs = set()

categories = [
    {"lang": "fr", "prefix": "https://www.albiaanews.com.tn/category/", "paths": [
        ('agriculture-fr/securite-alimentaire', 3),
        ('changement-climatique', 9),
        ('leau', 3),
        ('lenvironnement/economie-verte/energie-renouvelable', 2),
        ('lenvironnement/economie-verte', 4), 
        ('responsabilite-sociale-des-entreprises', 3)
    ]},
    {"lang": "ar", "prefix": "https://www.albiaanews.com.tn/ar/category/", "paths": [
        ('rse', 67), 
        ('التنمية-المستدامة', 16),
        ('البيئة/الأقتصاد-الأخضر/الطاقات-المتجددة', 27),
        ('الماء', 80),
        ('الفلاحة/الأمن-الغذائي', 27),
        ('التغيرات-المناخية', 58)   
    ]}
]

# Collect the articles from the categories 
for group in categories:
    for path, max_p in group["paths"]:
        for p in range(1, max_p + 1):
            link = f"{group['prefix']}{path}/page/{p}"
            print("Getting URLs from:", link)
            try: 
                response = requests.get(link, verify=False)
                response.encogind = 'utf-8'
                soup = BeautifulSoup(response.content)
                for i in soup.find_all('h2', {'class': 'entry-title fusion-post-title'}):
                    href = i.find('a')
                    if href and href['href']:
                        direct_URLs.add(href['href'])
                print(f"Now scraped {len(direct_URLs)} articles ...")
            except Exception as e:
                print("Error fetching page:", e)
    print(f"Total collected URLs: {len(direct_URLs)}")

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
            """
            # Extract date 
            if not article.get('date_publish'):
            # French
                h2 = soup.find('h2', {'class': 'title-heading-center'})
                if h2:
                    article['date_publish'] = dateparser.parse(h2.text.strip(), languages=['fr'])
                else:
                    # Arabic
                    div = soup.find('div', {'class': 'fusion-meta-info-wrapper'})
                    if div:
                        text = div.text.strip()
                        iso_match = re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\+\d{2}:\d{2}|Z)?', text)
                        if iso_match:
                            article['date_publish'] = dateparser.parse(iso_match.group())
                        else:
                            article['date_publish'] = dateparser.parse(text, languages=['ar'])
            
            try:
                date = soup.find('meta', {'itemprop': "datePublished"})['content']
                print(date)
                article['date_publish'] = dateparser.parse(date)
            except:
                try:
                    date = soup.find('h2', class_='title-heading-center').text.strip()
                    print(date)
                    article['date_publish'] = dateparser.parse(date, languages=['fr'])
                except:
                    try:
                        # Try Arabic version: <p class='fusion-single-line-meta'>...مايو 27th, 2023|</p>
                        date = soup.find('p', {'class': 'fusion-single-line-meta'}).text.strip()
                        article['date_publish'] = dateparser.parse(date, languages=['ar'])
                    except:
                        print("No date found")
            """

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
