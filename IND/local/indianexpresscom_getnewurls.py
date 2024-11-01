"""
Created on Nov 3, 2022 

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

source = 'indianexpress.com'
sitemap_base = 'https://indianexpress.com/sitemap.xml?yyyy='

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    
final_count = 0
final_inserted_url_count =0

for year in range(2014, 2024):
    year_str = str(year)
    
    # scraping by month
    for month in range(1, 13):
        if month < 10:
            month_str = '0' + str(month)
        else:
            month_str = str(month)
        
        for day in range(1, 32):
            direct_URLs = []
            if day < 10:
                day_str = '0' +str(day)
            else:
                day_str = str(day)

            print('Now scraping', str(year), str(month), str(day), '...')

            sitemap = sitemap_base + year_str +'&mm=' + month_str + '&dd=' + day_str 
            print(sitemap)
            
            req = requests.get(sitemap, headers = headers)
            soup = BeautifulSoup(req.content)
            # time.sleep(1)

            for i in soup.find_all('loc'):
                direct_URLs.append(i.text)
            print('Now collected',len(direct_URLs), 'URLs')

            blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
            blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
            direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]
            direct_URLs = [i for i in direct_URLs if "/opinion/" in i]

            final_result = list(set(direct_URLs))

            print('Total articles collected from current ', year_str, month_str)
            final_count += len(final_result) 

            inserted_url_count = 0
            processed_url_count = 0

            for url in final_result:
                print(url)
                try:
                    req = requests.get(url, headers = headers)
                    soup = BeautifulSoup(req.content)
                    # time.sleep(1)
                    article = NewsPlease.from_html(req.text, url=url).__dict__
                    
                    # add on some extras
                    article['date_download']=datetime.now()
                    article['download_via'] = "Direct2"
                    article['source_domain'] = source

                    print("newsplease title: ", article['title'])
                        
                    print("newsplease date: ", article['date_publish'])
                
                    if article['maintext']:
                        print("newsplease maintext: ", article['maintext'][:50])
                except:
                    print('Connection error, continue with next article...')
                    continue

               
                # add to DB
                else:
                    try:
                        year = article['date_publish'].year
                        month = article['date_publish'].month
                        if '/opinion/' in url:
                            article['primary_location'] = 'IND'
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
                        inserted_url_count += 1
                        print("Inserted! in ", colname, " - number of urls so far: ", inserted_url_count)
                    db['urls'].insert_one({'url': article['url']})
                except DuplicateKeyError:
                    pass
                    print("DUPLICATE! Not inserted.")
                    
                processed_url_count +=1    
                print('\n',processed_url_count, '/', len(final_result) , 'articles published in',year_str, month_str, ' have been processed ...\n')

            final_inserted_url_count += inserted_url_count
            

print("out of",final_count," urls, done inserting ", final_inserted_url_count, " from ",  source, " into the db.")
        



