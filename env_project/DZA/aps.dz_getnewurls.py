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

source = 'aps.dz'
direct_URLs = set()
base_url = 'https://www.aps.dz'

for p in range(0, 90, 10):
    link = 'https://www.aps.dz/ar/algerie/tag/%D9%88%D8%B2%D8%A7%D8%B1%D8%A9%20%D8%A7%D9%84%D8%A8%D9%8A%D8%A6%D8%A9?start=' + str(p) + '/'
    print("Getting urls from: ",link)
    response = requests.get(link, verify=False)
    # response.encoding = 'utf-8'

    soup = BeautifulSoup(response.content)
    for i in soup.find_all('h2', {'class' : 'tagItemTitle'}):
        a_tag = i.find('a')
        if a_tag and 'href' in a_tag.attrs:
            href = a_tag['href'] 

        # Build the correct URL 
            if href.startswith('/'):
                full_url = base_url + href
            elif not href.startswith('http'):
                full_url = f"{base_url}/{href.lstrip('/')}" # Ensure avoiding double slashes
            else:
                full_url = href 
        direct_URLs.add(full_url)

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
            # Extract using NewsPlease
            try:
                article = NewsPlease.from_html(response.text, url=url).__dict__
            except Exception as e:
                print(f"NewsPlease extraction error: {e}")
                article = {'title': None, 'date_publish': None, 'maintext': None}
            
            # Extract main text manually if needed
            maintext = ""
            item_full_text = soup.find('div', {'class': 'itemFullText'})
            if item_full_text:
                maintext = item_full_text.text.strip()
            else:
                paragraphs = [p.text.strip() for div in soup.find_all('div', {'class': 'itemFullText'}) for p in div.find_all('p', {'dir': 'rtl'})]
                if paragraphs:
                    maintext = "\n".join(paragraphs)
            
            if not maintext:
                paragraphs = [p.text.strip() for p in soup.find_all('p') if any('\u0600' <= c <= '\u06FF' for c in p.text)]
                maintext = "\n".join(paragraphs) if paragraphs else ""
            
            article['maintext'] = maintext or article.get('maintext', '')
    
            # Extract title manually if needed
            title_element = soup.find('h2', {'class': 'itemTitle'})
            if title_element:
                article['title'] = title_element.text.strip()
            elif not article['title']:
                for title_tag in soup.find_all(['h1', 'h2', 'h3']):
                    if title_tag.get('class') and any('title' in c.lower() for c in title_tag.get('class')):
                        article['title'] = title_tag.text.strip()
                        break

            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            article['url'] = url
            article['environmental'] = True
            
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
