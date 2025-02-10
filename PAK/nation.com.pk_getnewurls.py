#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sep 11 2023

@author: Hanling
 
"""
# Packages:
import sys
sys.path.append('../')
from pymongo import MongoClient
from urllib.parse import urlparse
from datetime import datetime
from pymongo.errors import DuplicateKeyError
import requests
from newsplease import NewsPlease
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import dateparser
import json

import calendar


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## NEED TO DEFINE SOURCE!
source = 'nation.com.pk'

# sitemap
base = 'https://www.nation.com.pk/archives/'


category = ['headlines', 'latest', 'national', 'international', 'lahore', 'karachi', 'islamabad']
# category = ['editorials']
year = range(2024, 2025)

month_str = []
for i in range(9, 12):
    month_str.append(calendar.month_abbr[i] )

day = range(1, 32)


url_count = 0
processed_url_count = 0
len_final_result = 0


for yy in year:
    yyyy = str(yy)
    for mm in month_str:
        direct_URLs = []
        print('Now scraping ', yyyy, mm )
        for dd in day:
            if dd < 10: 
                dd = '0' + str(dd)
            else:
                dd = str(dd)
            
            for c in category:
                date_str = dd + '-' + mm +'-' + yyyy +'/'
                url = base + date_str + c
                print(url)
                req = requests.get(url, headers = headers)
                soup = BeautifulSoup(req.content)
                item = soup.find_all('h3', {'class' : 'jeg_post_title category-page-title'})
                for i in item:
                    direct_URLs.append(i.find('a')['href'])
        print('Now scraped ', len(direct_URLs), ' articles from current month ...')

        final_result = direct_URLs.copy()

        len_final_result += len(final_result)

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

                    ## Fixing Date:
                    soup = BeautifulSoup(response.content, 'html.parser')
                        
                    if article['maintext']:
                        print('Maintext modified: ', article['maintext'][:50])
                                

                    try:
                        year = article['date_publish'].year
                        month = article['date_publish'].month
                        if c == 'editorials':
                            colname = f'opinion-articles-{year}-{month}'
                        else:
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
                        db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        # db[colname].delete_one({'url' : article['url']})
                        # db[colname].insert_one(article)
                        pass
                        print("DUPLICATE! Not inserted.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
                processed_url_count += 1
                print('\n',processed_url_count, '/', len_final_result, 'articles have been processed ...\n')

            else:
                pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")

