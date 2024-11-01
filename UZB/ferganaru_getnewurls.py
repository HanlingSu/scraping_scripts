"""
Created on Nov 1, 2022 

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

source = 'fergana.ru'

base = 'https://fergana.ru/news/'


url_count = 0
processed_url_count = 0

#132033 
# 132264
start = 131329
end = 132033

for i in range(end, start, -1):
    url = base + str(i)
    print(url)
    hdr = {'User-Agent': 'Mozilla/5.0'} #header settings

    req = requests.get(url, headers = hdr)
    soup = BeautifulSoup(req.content)
    article = NewsPlease.from_html(req.text, url=url).__dict__
    
    # add on some extras
    article['date_download']=datetime.now()
    article['download_via'] = "Direct2"
    article['source_domain'] = source
    
    # balcklist by category:
    category = []
    try:
        for c in soup.find_all('a', {'class' :'main-top-links-list__link'}, {'style' : None}):
            category.append(c.text)
    except:
        category = ['News']
    uninterested = False
    for c in category:
        if c in ['Спорт', 'Культура', 'История']:
                # sports, culture, history
            uninterested = True
        else:
            pass
            
    if uninterested: 
        article['title'] = "From uninterested category"
        article['date_publish'] = None
        article['maintext'] = None
        print(article['title'])

    else:
        print("newsplease title: ", article['title'])
           
        # fix date
        try:
            date = soup.find('span', {'class' :'main-top-links-list__text', 'style' : None}).text.replace('msk', '').strip()
            article['date_publish'] = dateparser.parse(date, settings= {'DATE_ORDER' : 'DMY'})
        except:
            article['date_publish'] = article['date_publish'] 
        print("newsplease date: ", article['date_publish'])

        # fix maintext
        try:
            maintext = ''
            for i in soup.find('div',{ "class" : 'article-content article-content--narrow'}).find_all('p'):
                maintext += i.text
            article['maintext'] = maintext
        except:
            article['maintext'] = article['maintext']
        if article['maintext']:
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
                url_count = url_count + 1
                print("Inserted! in ", colname, " - number of urls so far: ", url_count)
            db['urls'].insert_one({'url': article['url']})
        except DuplicateKeyError:
            pass
            print("DUPLICATE! Not inserted.")
            
        processed_url_count += 1
        print('\n',processed_url_count, '/', str(end-start) , 'articles have been processed ...\n')


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
    