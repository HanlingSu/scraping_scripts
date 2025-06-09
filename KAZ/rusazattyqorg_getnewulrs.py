###### Packages:

from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from pymongo import MongoClient
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import cloudscraper

import sys
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import dateparser
from pymongo.errors import DuplicateKeyError
from tqdm import tqdm
import re
import sys
import json
import time
import detectlanguage
import json
import pymongo

db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

detectlanguage.configuration.api_key = "81762acd6a7244ef736911adbadb09e3"

start = 1
end = 40

direct_URLs = []
hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

source = 'rus.azattyq.org'
for i in range( start, end + 1):
    url = 'https://rus.azattyq.org/z/360?p=' + str(i) 

    req = requests.get(url, headers = hdr)
    soup = BeautifulSoup(req.content)

    for i in soup.find('div', {'class' : 'news'}).find_all('div', {'class'  : 'news__item news__item--unopenable accordeon__item sticky-btn-parent'}):
        direct_URLs.append(i['data-article-id'])
    print('Now collected', len(direct_URLs), 'articles ... ')
direct_URLs= [ 'https://rus.azattyq.org/a/' + i +'.html'for i in direct_URLs]
final_result = list(set(direct_URLs))

print(len(final_result))

url_count = 0
processed_url_count = 0


for url in final_result:
    print(url, "FINE")
    ## SCRAPING USING NEWSPLEASE:
    try:
        #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
        header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        req = requests.get(url, headers = hdr)
        soup = BeautifulSoup(req.content)
            
        article = NewsPlease.from_html(req.text, url=url).__dict__
        
        # add on some extras
        try:
            audionews = soup.find('h1', {'class' : 'title pg-title title--program'}).text
        except:
            audionews = None

        if audionews  in ['Аудионовости', 'رادیو ژورنال']:
            article['title'] = 'From audio news'
            article['date_publish'] = None

        else:
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
        
            
            print("newsplease title: ", article['title'])

            print("newsplease date: ", article['date_publish'])
            

            if not article['maintext']:
                try:
                    maintext = ''
                    for i in soup.find('div', {'id' : 'article-content'}).find_all('p'):
                        maintext += i.text
                    article['maintext'] = maintext.strip()
                except:
                    try:
                        article['maintext'] = soup.find('div', {'class' : 'intro'}).text
                    except:
                        maintext = ''
                        for i in soup.find_all('p'):
                            maintext += i.text
                        article['maintext'] = maintext.strip()
                        
            print("newsplease maintext: ", article['maintext'][:50])
    except:
        continue

    # add to DB
    try:
        year = article['date_publish'].year
        month = article['date_publish'].month
        colname = f'articles-{year}-{month}'
        
    except:
        colname = 'articles-nodate'
    
    # if colname != 'articles-nodate':
    #     code = detectlanguage.detect(article['maintext'])[0]['language']
    #     article['language'] = code
    #     print('News article is in',article['language'] )
    # Inserting article into the db:
    try:
        db[colname].insert_one(article)
        # count:
        if colname != 'articles-nodate':
            url_count += 1
            print("Inserted! in ", colname, " - number of urls so far: ", url_count)
        db['urls'].insert_one({'url': article['url']})
    except DuplicateKeyError:
        pass
        print("DUPLICATE! Not inserted.")
        
    processed_url_count +=1    
    print('\n',processed_url_count, '/', len(final_result) , 'articles have been processed ...\n')

    

print("Done inserting ", processed_url_count, " manually collected urls from ",  source, " into the db.")
    
