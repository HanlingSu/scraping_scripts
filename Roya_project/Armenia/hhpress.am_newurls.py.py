import bs4
from bs4 import BeautifulSoup
from newspaper import Article
from dateparser.search import search_dates
import dateparser
import requests
from urllib.parse import quote_plus

import urllib.request
import time

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
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from dotenv import load_dotenv

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'hhpress.am'

hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
categories = ['mijazgayin', 'spyurq', 'hanrapetutyun', 'socium']
page_start = [1, 1, 1, 1]
page_end = [99, 12, 104, 95]

for c, ps, pe in zip(categories, page_start, page_end):
    for p in range(ps, pe+1):
        direct_URLs = []
        url = 'https://hhpress.am/category/' +c +'/page/' +str(p)
        print(url)
        req = requests.get(url, headers = hdr)
        soup = BeautifulSoup(req.content)
        for i in soup.find_all('h3', {'class' : 'jeg_post_title'}):
            direct_URLs.append(i.find('a')['href'])
        print('Now collected ', len(direct_URLs), 'URLs...')

        final_result = list(set(direct_URLs))

        print(len(final_result))

        url_count = 0
        processed_url_count = 0

        for url in final_result:
            if url:
                print(url, "FINE")
                ## SCRAPING USING NEWSPLEASE:
                try:
                    #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
                    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                    response = requests.get(url, headers=hdr)
                    article = NewsPlease.from_html(response.text, url=url).__dict__
                    # add on some extras
                    article['date_download']=datetime.now()
                    article['download_via'] = "Direct2"
                    article['source_domain'] = source
                    
                    soup = BeautifulSoup(response.content, 'html.parser')

            

                    print("newsplease date: ", article['date_publish'])
                    print("newsplease title: ", article['title'])

                    try:
                        maintext = ''
                        for i in soup.find('div', {'class' : 'content-inner'}).find_all('p'):
                            maintext += i.text
                        article['maintext'] = maintext.strip()
                    except:
                        try:
                            maintext = ''
                            for i in  soup.find_all('p')[2:]:
                                maintext += i.text
                            article['maintext'] = maintext.strip()
                        except:
                            article['maintext'] =article['maintext'] 
                    if article['maintext']:
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



