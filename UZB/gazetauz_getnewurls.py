"""
Created on Nov 2, 2022 

Craated by Hanling Su
"""

# Packages:

from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from datetime import datetime
from pymongo.errors import DuplicateKeyError
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
import re
import json
import pandas as pd
import cloudscraper

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p


scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)

hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


source = 'gazeta.uz'
category = ['economy', 'politics', 'society', 'world']
base = 'https://www.gazeta.uz/oz/'

page_start = [1, 1, 1, 1]
page_end = [0, 0, 60, 13]
final_count = 0
final_inserted_url_count =0
direct_URLs = []

for c, ps, pe in zip(category, page_start, page_end):
    for p in range(ps, pe+1):
        link = base + c +'?page=' +str(p)
        print(link)
        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings

        soup = BeautifulSoup(scraper.get(link).text)

        for i in soup.find_all('h3'):
            direct_URLs.append(i.find('a')['href'])
        print('Now collected',len(direct_URLs), 'URLs')

    direct_URLs = ['https://www.gazeta.uz' + i for i in direct_URLs]
    final_result = direct_URLs.copy()
    final_count += len(final_result)
    print('Total articles collected', len(final_result))

    inserted_url_count = 0
    processed_url_count = 0

    for url in final_result:
        print(url)
        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings

        soup = BeautifulSoup(scraper.get(url).text)
        article = NewsPlease.from_html(scraper.get(url).text).__dict__

        
        # add on some extras
        article['date_download']=datetime.now()
        article['download_via'] = "Direct2"
        article['source_domain'] = source
        article['url'] = url

        # balcklist by category:
       
    
        print("newsplease title: ", article['title'])

        # fix date
        try:
            date = soup.find('meta', itemprop = 'datePublished')['content']
            article['date_publish'] = dateparser.parse(date).replace(tzinfo=None)
        except:
            article['date_publish'] = article['date_publish'] 
        print("newsplease date: ", article['date_publish'])

        # fix maintext
        if not article['maintext']:
            try:
                maintext = ''
                for i in soup.find('div', {'itemprop' :'articleBody'}).find_all('p'):
                    maintext += i.text
                article['maintext'] = maintext.strip()
            except:
                article['maintext'] = None

            if article['maintext']:
                print("newsplease maintext: ", article['maintext'][:50])
        else:
            print("newsplease maintext: ", article['maintext'][:50])

        # add to DB
        try:
            year = article['date_publish'].year
            month = article['date_publish'].month
            colname = f'articles-{year}-{month}'
            
        except:
            colname = 'articles-nodate'
        
        # Inserting article into the db:
        try:
            db[colname].insert_one(article)
            # count:
            if colname != 'articles-nodate':
                inserted_url_count +=  1
                print("Inserted! in ", colname, " - number of urls so far: ", inserted_url_count)
            db['urls'].insert_one({'url': article['url']})
        except DuplicateKeyError:
            pass
            print("DUPLICATE! Not inserted.")
        processed_url_count +=1    
        print('\n',processed_url_count, '/', len(final_result) , 'articles have been processed ...\n')

    final_inserted_url_count += inserted_url_count

print("Done inserting ", final_inserted_url_count, " manually collected urls from ",  source, " into the db.")
        
