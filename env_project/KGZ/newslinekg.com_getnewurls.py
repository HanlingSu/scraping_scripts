# Packages:
from pymongo import MongoClient
import re
import bs4
from bs4 import BeautifulSoup
from newspaper import Article
from dateparser.search import search_dates
import dateparser
import requests
from urllib.parse import quote_plus

import urllib.request
import time
from time import time
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
from newsplease import NewsPlease
from dotenv import load_dotenv
import cloudscraper 
from dateutil import parser as dateparser

scraper = cloudscraper.create_scraper(
    browser ={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    } 
)

hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'newslinekg.com'
base_url = 'https://newslinekg.com'

direct_URLs = set()

categories = (773)
pages = (653)

""" 
769 = Energy industry - 279
770 = Agriculture - 728
775 = Metals and Minerals - 1014
773 = Oil and Gas Sector - 653

""" 
url_count = 0
processed_url_count = 0
len_final_result = 0
header ={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'} #header settings

base = "https://newslinekg.com"
for year in range(2022, 2024):
    year_str = str(year)
    for month in range(1, 13):
        if month >= 10:
            month_str = str(month)
        else:
            month_str = '0'+str(month)
        for day in range(1, 32):
            direct_URLs = []
            if day >= 10:
                day_str = str(day)
            else:
                day_str = '0'+str(day)
            
            date_str = year_str + '-' +month_str +'-' +day_str
            link = base + '/' + date_str +'/'
            print(link)
            try:
                reqs = requests.get(link, headers=header)
                soup = BeautifulSoup(reqs.text, 'html.parser')
                for i in soup.find_all('h2', {'class' : 'zag_cn'}):
                    direct_URLs.append(i.find('a')['href'])
            except:
                pass

            final_result = [base + i for i in direct_URLs]
            len_final_result += len(final_result)

            for url in final_result:
                if url:
                    print(url, "FINE")
                    ## SCRAPING USING NEWSPLEASE:
                    try:
                        # process
                        soup = BeautifulSoup(scraper.get(url).text)
                        article = NewsPlease.from_html(scraper.get(url).text, url=url).__dict__

                        # add on some extras
                        article['date_download']=datetime.now()
                        article['download_via'] = "Direct2"
                        article['source_domain'] = source
                        article['url'] = url
                        article['environmental'] = True

                        # Extract date 
                        try:
                            date = date_str
                            print(date)
                            article['date_publish'] = dateparser.parse(date)
                        except:
                            article['date_publish'] = None

                        try:
                            maintext = ''
                            for i in soup.find('div', {'class' : 'news-detail'}).find_all('p'):
                                maintetx += i.text
                            article['maintext'] = maintext.strip()
                        except:
                            article['maintext'] = article['maintext'] 
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
                        try:
                            #TEMP: deleting the stuff i included with the wrong domain:
                            # myquery = { "url": final_url, "source_domain" : 'web.archive.org'}
                            # db[colname].delete_one(myquery)
                            # Inserting article into the db:
                            db[colname].insert_one(article)
                            # count:
                            url_count = url_count + 1
                            print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                            db['urls'].insert_one({'url': article['url']})
                        except DuplicateKeyError:
                            print("DUPLICATE! Not inserted.")
                    except Exception as err: 
                        print("ERRORRRR......", err)
                        pass
                    processed_url_count += 1
                    print('\n',processed_url_count, '/', len_final_result, 'articles have been processed ...\n')
            
                else:
                    pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
