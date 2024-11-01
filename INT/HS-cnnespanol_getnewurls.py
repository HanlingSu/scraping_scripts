"""
Created on May 21 2024

@author: Hanling

This script updates 'cnnespanol.cnn.com' using sitemap.
It can be run as often as one desires. 

 
"""
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
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from dotenv import load_dotenv

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []

base = "https://cnnespanol.cnn.com/post-sitemap"

for p in range(153, 155):
    link = base + str(p) +'.xml'
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = requests.get(link, headers = hdr)
    soup = BeautifulSoup(req.content)
    for i in soup.find_all('loc'):
        direct_URLs.append(i.text)
    print("Now collected ", len(direct_URLs), "articles ... ")


direct_URLs =list(set(direct_URLs))
# direct_URLs = pd.read_csv('Downloads/peace-machine/peacemachine/getnewurls/INT/cnnespanol.csv')['url']

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
            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            response = requests.get(url, headers=header)
            # process
            article = NewsPlease.from_html(response.text, url=url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            #print("newsplease date: ", article['date_publish'])

            soup = BeautifulSoup(response.content, 'html.parser')

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
                #print(article)
            except:
                colname = 'articles-nodate'
            #print("Collection: ", colname)
            try:
                #TEMP: deleting the stuff i included with the wrong domain:
                #myquery = { "url": final_url, "source_domain" : 'web.archive.org'}
                #db[colname].delete_one(myquery)
                # Inserting article into the db:
                db[colname].insert_one(article)
                  # count:
                if colname != 'articles-nodate':
                    url_count = url_count + 1
                    print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                else:
                    print("Inserted! in ", colname)
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
