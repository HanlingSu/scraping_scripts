
"""
Created on Nov 7, 2022 

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
import time


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'hindustantimes.com'
sitemap_base = 'https://www.hindustantimes.com/sitemap/'


final_count = 0
final_processed_url_count = 0
final_inserted_url_count =0

hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

for year in range(2012, 2024):
    year_str = str(year)
    for month in range(1, 13):
        direct_URLs = []
        month_str = datetime.strptime(str(month), "%m").strftime("%B").lower()
        print('Now scraping', str(year), str(month), '...')

        sitemap = sitemap_base + month_str + '-' + year_str +'.xml'
        print(sitemap)
  


        req = requests.get(sitemap, headers = hdr)
        soup = BeautifulSoup(req.content)

        for i in soup.find_all('loc'):
            direct_URLs.append(i.text)
        print('Now collected',len(direct_URLs), 'URLs')


        # blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
        # blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
        # direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]
        direct_URLs = [i for i in direct_URLs if  '/analysis/' in i or '/opinion/' in i]
        final_result = list(set(direct_URLs))
       
        final_count += len(final_result)
        print('Total articles collected', len(final_result))

        inserted_url_count = 0
        processed_url_count = 0

        for url in final_result:
            print(url)
            try:
            
                req = requests.get(url, headers = hdr)
                soup = BeautifulSoup(req.content)
            
            
                article = NewsPlease.from_html(req.text, url=url).__dict__
                
                # add on some extras
                article['date_download']=datetime.now()
                article['download_via'] = "Direct2"
                article['source_domain'] = source
            
                
                print("newsplease title: ", article['title'])
                # fix date

                try:
                    date = soup.find('meta', property = 'article:published_time')['content']
                    article['date_publish'] = dateparser.parse(date)
                except:
                    article['date_publish'] =article['date_publish']
                print("newsplease date: ", article['date_publish'])
                

                if article['maintext']:
                    print("newsplease maintext: ", article['maintext'][:50])
            except:
                continue
            
            if '/analysis/' in url or '/opinion/' in url:
                try:
                    year = article['date_publish'].year
                    month = article['date_publish'].month
                    article['primary_location'] = "IND"
                    colname = f'opinion-articles-{year}-{month}'
                    
                except:
                    colname = 'articles-nodate'
            else:
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
    
