"""
Created on Oct 24, 2022 

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


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'nyasatimes.com'


# final_result = list(pd.read_csv('Downloads/peace-machine/peacemachine/getnewurls/MWI/nyasatimescom.csv')['0'])

base = 'https://www.nyasatimes.com/category/'

category = ['national', 'politics', 'columns', 'education', 'health', 'news']
page_start = [1, 1, 1, 1, 1, 1] 
page_end = [0,0,3,0,0,0] #30, 8, 5, 5, 3, 25

direct_URLs = []
for c, ps, pe in zip(category, page_start, page_end):
    for p in range(ps, pe+1):
        url = base + c + '/page/' +str(p)
        print(url)
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = requests.get(url, headers = hdr)
        soup = BeautifulSoup(req.content)
        for i in soup.find_all('div', {'class' : 'card-main-title'}):
            direct_URLs.append(i.find('a')['href'])
        print('Now collected',len(direct_URLs), 'URLs')

final_result = list(set(direct_URLs))

url_count = 0
processed_url_count = 0
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

            # blacklist by category
            soup = BeautifulSoup(response.content, 'html.parser')

            try: 
                category = json.loads(soup.find('script', type = 'application/ld+json').contents[0])['@graph'][0]['articleSection'].split(', ')

            except:
                category = ['News']

            
            for c in category:
                if c in ['Entertainment', 'Religion, Religious News', 'Sports']:
                    article['date_publish'] = None
                    article['maintext'] = None
                    article['title'] = "From uninterested category" + c
                    print('From category:', c)
                    pass
                
            print("From categort",  category)

            if article['date_publish']:
                print("newsplease date: ", article['date_publish'])
            print("newsplease title: ", article['title'])
            if article['maintext']:
                print("newsplease maintext: ", article['maintext'][:50])

      
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                if 'Columns' in category:
                    colname = f'opinion-articles-{year}-{month}'
                else:
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
