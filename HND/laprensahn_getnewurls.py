#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Nov 17 2021

@author: Hanling Su

This script updates laprensa.hn using daily sitemaps.
It MUST BE RUN EVERY DAY.
 
"""
# Packages:
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
from datetime import datetime
from pymongo.errors import DuplicateKeyError
import requests
from newsplease import NewsPlease
from dotenv import load_dotenv
import re

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## COLLECTING URLS
direct_URLs = []

## NEED TO DEFINE SOURCE!
source = 'laprensa.hn'

base_list = []

base = 'https://www.laprensa.hn/busquedas/-/search/e/false/false/20250101/20250301/date/true/true/0/0/meta/0/0/0/'

hdr = {'User-Agent': 'Mozilla/5.0'} #header settings

for i in range(349, 522):
    base_list.append(base + str(i))

print('Scrape ', len(base_list), ' page of search result for ', source)

direct_URLs = []
for b in base_list:
    print(b)
    try: 
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = requests.get(b, headers = headers)
        soup = BeautifulSoup(req.content)
        
        item = soup.find_all('div', {'class' : 'card-title title'})
        for i in item:
            url = i.find('a', href=True)['href']
            if url:
                direct_URLs.append(url)
        print('Now scraped ', len(direct_URLs), ' articles from previous page.')
    except:
        pass


blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

direct_URLs = ['https://www.laprensa.hn' + i for i in direct_URLs]
print(direct_URLs[:5])
direct_URLs = direct_URLs.copy()
print('Total number of urls found: ', len(direct_URLs))


final_result = direct_URLs

## INSERTING IN THE DB:
url_count = 0
source = 'laprensa.hn'
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
            print("newsplease date: ", article['date_publish'])
            print("newsplease title: ", article['title'])
            print("newsplease maintext: ", article['maintext'][:50])


            ## Fixing Date:
            soup = BeautifulSoup(response.content, 'html.parser')
           

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
                url_count = url_count + 1
                print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                db['urls'].insert_one({'url': article['url']})
            except DuplicateKeyError:
                print("DUPLICATE! Not inserted.")
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
