import bs4
from bs4 import BeautifulSoup
from newspaper import Article
from dateparser.search import search_dates
import dateparser
import requests
from urllib.parse import quote_plus

import urllib.request
import time

import random
from random import randint, randrange
from warnings import warn
import json
from pymongo import MongoClient
from urllib.parse import urlparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from pymongo.errors import CursorNotFound
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from dotenv import load_dotenv

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

url_count = 0
processed_url_count = 0
len_final_result = 0
source = 'magyarnemzet.hu'


for year in range(2020, 2024):
    year_str = str(year)
    for month in range(1, 13):

        direct_URLs = []
        
        if month <10:
            month_str = '0' + str(month)
        else:
            month_str =  str(month)
        
        url = 'https://magyarnemzet.hu/'+ year_str + month_str + '_sitemap.xml'
        hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

        req = requests.get(url, headers = hdr)
        soup = BeautifulSoup(req.content)

        for i in soup.find_all('loc'):
            direct_URLs.append(i.text)

        final_result = direct_URLs.copy()
        len_final_result += len(final_result)

        for url in final_result:
            if url:
                print(url, "FINE")
                ## SCRAPING USING NEWSPLEASE:
                try:
                    hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

                    req = requests.get(url, headers = hdr)
                    soup = BeautifulSoup(req.content)

                    article = NewsPlease.from_html(req.text, url=url).__dict__
                    # add on some extras
                    article['date_download']=datetime.now()
                    article['download_via'] = "Direct2"
                    article['source_domain'] = source

                        
                   

                    print("newsplease date: ", article['date_publish'])
                    print("newsplease title: ", article['title'])
                    print("newsplease maintext: ", article['maintext'][:50])

                    try:
                        year = article['date_publish'].year
                        month = article['date_publish'].month
                        colname = f'articles-{year}-{month}'
                        #print(article)
                    except:
                        colname = 'articles-nodate'
                    #print("Collection: ", colname)
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
                    print("ERRORRRR......", err, 'Inserted to error urls ....')
                    
                    pass
                processed_url_count += 1
                print('\n',processed_url_count, '/', len_final_result, 'articles have been processed ...\n')
        
            else:
                pass


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
