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

source = 'kun.uz'
sitemap_base = 'https://kun.uz/sitemap/sitemap-news_article_'
direct_URLs = pd.read_csv('/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/UZB/kun.csv')['0']

final_count = 0
final_processed_url_count = 0
final_inserted_url_count =0

# for year in range(2024, 2025):
#     for month in range(6, 9):
#         print('Now scraping', str(year), str(month), '...')
#         for day in range(1, 32):
#             direct_URLs = []
#             sitemap = sitemap_base + str(year) +'_' +str(month) + '_' + str(day)  + '.xml'
#             # print(sitemap)
#             hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    
#             req = requests.get(sitemap, headers = hdr)
#             soup = BeautifulSoup(req.content)

#             for i in soup.find_all('loc'):
#                 direct_URLs.append(i.text)
#             print('Now collected',len(direct_URLs), 'URLs')

final_result = list(set(direct_URLs))
final_count += len(final_result)
print('Total articles collected', len(final_result))

inserted_url_count = 0
processed_url_count = 0

for url in final_result:
    print(url)
    hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


    req = requests.get(url, headers = hdr)
    soup = BeautifulSoup(req.content)
    article = NewsPlease.from_html(req.text, url=url).__dict__
    
    # add on some extras
    article['date_download']=datetime.now()
    article['download_via'] = "Direct2"
    article['source_domain'] = source


    # balcklist by category:
    try:
        category = soup.find('a', {'class' :'news__category'}).text
    except:
        category = 'News'

    uninterested = False
    
    if category in ['Спорт', 'Ўзбекистон', 'Ўзбекистон']:
            # sports, tech, business class
        uninterested = True
    else:
        pass
            
    if uninterested: 
        article['title'] = "From uninterested category"
        article['date_publish'] = None
        article['maintext'] = None
        print(article['title'], '\n')

    else:
    
        print("newsplease title: ", article['title'])
        # fix date
        try:
            date = soup.find('div', {'class' :'single-header__meta'}).find('div', {'class' : 'date'}).text
            article['date_publish'] = dateparser.parse(date, settings= {'DATE_ORDER' : 'DMY'})
        except:
            article['date_publish'] = article['date_publish'] 
        print("newsplease date: ", article['date_publish'])

        # fix maintext
        try:
            maintext = ''
            for i in soup.find('div', {'class' :'news-inner__content-page'}).find_all('p'):
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
                inserted_url_count += 1
                print("Inserted! in ", colname, " - number of urls so far: ", inserted_url_count)
            db['urls'].insert_one({'url': article['url']})
        except DuplicateKeyError:
            pass
            print("DUPLICATE! Not inserted.")
            
        processed_url_count +=1    
        print('\n',processed_url_count, '/', len(final_result) , 'articles have been processed ...\n')

final_inserted_url_count += inserted_url_count
final_processed_url_count += processed_url_count

print('\n',final_processed_url_count, '/', final_count , 'articles have been processed ...\n')

print("Done inserting ", final_inserted_url_count, " manually collected urls from ",  source, " into the db.")

