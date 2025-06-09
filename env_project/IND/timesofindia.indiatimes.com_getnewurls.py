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

source = 'timesofindia.indiatimes.com'
direct_URLs = set()
base_url = 'https://timesofindia.indiatimes.com'

for p in range(2, 51):
    link = 'https://timesofindia.indiatimes.com/home/environment/' + str(p) 
    print("Getting urls from: ", link)

    response = requests.get(link, verify=False)
    soup = BeautifulSoup(response.content)

    for i in soup.find_all('span', {'class': 'w_tle'}):
        a_tag = i.find('a')
        if a_tag and a_tag.get('href'):
            href = a_tag.get('href')
            url = base_url + href
            direct_URLs.add(url)

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

            #Extract date: 
            try:
                byline_div = soup.find('div', {'class': 'xf8Pm byline'})
                if byline_div:
                    date_text = byline_div.get_text(strip=True)

                    # Case 1: "Updated: Nov 28, 2024, 21:30 IST"
                    if "Updated:" in date_text:
                        date_clean = date_text.split("Updated:")[-1].strip()
                        article['date_publish'] = dateparser.parse(date_clean)

                    # Case 2: "Vishwa Mohan / TNN / Nov 19, 2024, 09:34 IST"
                    elif "/" in date_text:
                        parts = [p.strip() for p in date_text.split("/") if p.strip()]
                        if parts and dateparser.parse(parts[-1]):
                            article['date_publish'] = dateparser.parse(parts[-1])
                        else:
                            article['date_publish'] = None

                    # Case 3: Only <span> contains date
                    else:
                        span = byline_div.find('span')
                        if span:
                            date_clean = span.get_text(strip=True).replace("Updated:", "").strip()
                            article['date_publish'] = dateparser.parse(date_clean)
                        else:
                            article['date_publish'] = None
                else:
                    article['date_publish'] = None
            except Exception as e:
                print(f"Date parsing failed: {e}")
                article['date_publish'] = article.get('date_publish', None)



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
