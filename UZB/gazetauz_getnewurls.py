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


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'gazeta.uz'
sitemap_base = 'https://www.gazeta.uz/sitemap/materials-ru-'


final_count = 0
final_inserted_url_count =0

for year in range(2024, 2025):
    year_str = str(year)
    direct_URLs = []
    for month in range(5, 6):
        if month < 10:
            month_str = '0' + str(month)
        else:
            month_str = str(month)
        print('Now scraping', str(year), str(month), '...')
        for day in range(1, 32):
            if day < 10:
                day_str = '0' +str(day)
            else:
                day_str = str(day)

            sitemap = sitemap_base + year_str +'-' + month_str + '-' + day_str + '.xml'
            # print(sitemap)
            hdr = {'User-Agent': 'Mozilla/5.0'} #header settings

            req = requests.get(sitemap, headers = hdr)
            soup = BeautifulSoup(req.content)

            for i in soup.find_all('loc'):
                direct_URLs.append(i.text)
        print('Now collected',len(direct_URLs), 'URLs')

    final_result = direct_URLs.copy()
    final_count += len(final_result)
    print('Total articles collected', len(final_result))

    inserted_url_count = 0
    processed_url_count = 0

    for url in final_result:
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
        try:
            category = soup.find('div', {"class" : 'articleDateTime'}).find('a').text
        except:
            category = 'News'

        uninterested = False
        
        if category in ['Спорт']:
                # sports, 
            uninterested = True
        else:
            pass
                
        if uninterested: 
            article['title'] = "From uninterested category"
            article['date_publish'] = None
            article['maintext'] = None
            print(article['title'], category)

        else:
        
            print("newsplease title: ", article['title'])

            # fix date
            try:
                date = soup.find('meta', property = 'article:published_time')['content']
                article['date_publish'] = dateparser.parse(date).replace(tzinfo=None)
            except:
                article['date_publish'] = article['date_publish'] 
            print("newsplease date: ", article['date_publish'])

            # fix maintext
            if not article['maintext']:
                try:
                    maintext = ''
                    for i in soup.find('div', {'class' :'articleContent'}).find_all('p'):
                        maintext += i.text
                    article['maintext'] = maintext.strip()
                except:
                    try:
                        article['maintext'] = soup.find('h4', {'class' :None}).text.strip()
                    
                    except:
                        try:
                            article['maintext'] = soup.find('t-row').text.strip()
                        except:
                            try:
                                article['maintext'] = soup.find('div', {'class' : 't-col t-col_8 t-prefix_2'}).text.strip()
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
        
