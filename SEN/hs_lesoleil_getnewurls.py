

# Packages:
import sys
import os
import re
import getpass
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np 
from pymongo import MongoClient
import bs4
from bs4 import BeautifulSoup
from newspaper import Article
from dateparser.search import search_dates
import dateparser
import requests
import urllib.request
from warnings import warn
import json
from pymongo import MongoClient
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from pymongo.errors import CursorNotFound
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

base = 'https://lesoleil.sn/rubriques/'
source = 'lesoleil.sn'

category = ['actualites', 'international']
page_start = [0, 0]
page_end = [150, 30]

url_count = 0
processed_url_count = 0

for c, ps, pe in zip(category, page_start, page_end):
    for p in range(ps, pe+1):
        sitemap = base + c +'/page/' + str(p) 
        print(sitemap)
        direct_URLs = []

        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
        req = requests.get(sitemap, headers = hdr)
        soup = BeautifulSoup(req.content)
        try:
            item = soup.find('div', {'class' : 'elementor-loop-container elementor-grid'}).find_all('a', {'class' :'elementor-cta'})
            for i in item:
                url = i.find('a')['href']
                direct_URLs.append(url)
        except:
            pass
        print(len(direct_URLs))

        final_result = direct_URLs.copy()


        for url in final_result:
            if url:
                print(url, "FINE")
                ## SCRAPING USING NEWSPLEASE:
                try:
                    #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
                    header = hdr = {'User-Agent': 'Mozilla/5.0'}
                    response = requests.get(url, headers=header)
                    # process
                    article = NewsPlease.from_html(response.text, url=url).__dict__
                    # add on some extras
                    article['date_download']=datetime.now()
                    article['download_via'] = "Direct2"
                    article['source_domain'] = source
                    # title has no problem
                    
                    # custom parser
                    soup = BeautifulSoup(response.content, 'html.parser')
                
                        
                    print("newsplease date: ",  article['date_publish'])
                    print("newsplease title: ", article['title'])
                    print("newsplease maintext: ", article['maintext'][:50])
                
                    
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
                            url_count = url_count + 1
                            print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        pass
                        print("DUPLICATE! Not inserted.")
                        
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
                processed_url_count += 1
                print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')
        
            else:
                pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
