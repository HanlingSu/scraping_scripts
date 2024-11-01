"""
Created on Sep 5 

@author: Hanling

This script scrapes/updates 'deccanherald.com' using sitemaps. 

""" 
 
import random
import sys
import os
import re
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from pymongo.errors import CursorNotFound
import requests
from bs4 import BeautifulSoup
import pandas as pd
from newsplease import NewsPlease
from datetime import datetime
import dateparser
import time
import json

db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p



headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

source = 'deccanherald.com'


baseurl = 'https://www.deccanherald.com/sitemap/sitemap-daily-'

len_all_inserted_url_count = 0
len_final_urls = 0

years = range(2024, 2025)
months = range(7, 8)
days = range(19, 32)
direct_URLs = []
for year in years:
    year_str = str(year)
    for month in months:
        if month <10:
            month_str = '0' + str(month)
        else: 
            month_str = str(month)
        for day in days:
            if day <10:
                day_str = '0' + str(day)
            else: 
                day_str = str(day)

            url = baseurl + year_str + '-' + month_str +'-' +day_str +'.xml'
        
            print(url)
            reqs = requests.get(url, headers=headers)
            soup = BeautifulSoup(reqs.text, 'html.parser')
            for link in soup.find_all('loc'):
                direct_URLs.append(link.text)
        direct_URLs = list(set(direct_URLs))
        print(len(direct_URLs))
            
        blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
        blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
        direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

        monthly_result = direct_URLs.copy()
        print('Total articles collected from %s - %s : %s' % ( year_str,month_str, len(monthly_result)))
        len_final_urls += len(monthly_result)


        ## INSERTING IN THE DB:
        inserted_url_count = 0
        processed_url_count = 0
        for url in monthly_result:

            print(url)
            try:
                header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                response = requests.get(url, headers=header)
                article = NewsPlease.from_html(response.text, url=url).__dict__

                # add on some extras
                article['date_download']=datetime.now()
                article['download_via'] = "Direct2"
                article['source_domain'] = source
                print("newsplease title: ", article['title'])
                # article['maintext'] = article['maintext'].replace('JawaPos.com', '')
                # article['maintext'] = article['maintext'].split('-', 1)[1]

                ## Fixing Date:
                soup = BeautifulSoup(response.content, 'html.parser')
                try:
                    date = json.loads(soup.find_all('script', {'type':"application/ld+json"})[-1].contents[0])['datePublished']
                    article['date_publish'] = dateparser.parse(date).replace(tzinfo=None)
                except:
                    article['date_publish'] =article['date_publish'] 
                print("newsplease date: ", article['date_publish'])

                try:
                    maintext = ''
                    for i in soup.find_all('div', {'class' : 'story-element story-element-text'}):
                        maintext += (i.text)
                    article['maintext'] = maintext
                except:
                    article['maintext'] = article['maintext'] 
                print("newsplease maintext: ", article['maintext'][:50])


                # add on some extras
                article['date_download']=datetime.now()
                article['download_via'] = "Direct2" #change
                article['source_domain'] = source



                ## Inserting into the db
                try:
                    year = article['date_publish'].year
                    month = article['date_publish'].month
                    colname = f'articles-{year}-{month}'
                    #print(article)
                except:
                    colname = 'articles-nodate'

                try:
                    # Inserting article into the db:
                    db[colname].insert_one(article)
                    # count:
                    if colname != 'articles-nodate':
                        inserted_url_count = inserted_url_count + 1

                    print("Inserted! in ", colname, " - number of urls so far: ", inserted_url_count)
                except DuplicateKeyError:
                    print("DUPLICATE! Not inserted.")

                processed_url_count += 1
                print('\n',processed_url_count, '/', len(monthly_result), 'articles have been processed ...\n')

            except Exception as err: 
                print("ERRORRRR......", err)
                pass


        len_all_inserted_url_count += inserted_url_count

print("Done inserting ", len_all_inserted_url_count, "collected urls from ",  source, " into the db.")

