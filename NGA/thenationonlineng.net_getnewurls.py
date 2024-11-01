# Packages:
import pymongo 
from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import cloudscraper
import pandas as pd
from tqdm import tqdm
import re
import sys
import json
import time
    

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

source = 'thenationonlineng.net'


scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)

categories = ['politics', 'news']

base = 'https://thenationonlineng.net/'
           

# delete blacklist URLs

page_start = [1, 1]
page_end = [16, 500 ]
# 0,0,  700,1000


processed_url_count = 0
url_count = 0
len_final_result = 0


for c, ps, pe in zip(categories, page_start, page_end):
    for p in range(ps, pe +1):

        direct_URLs = []

        url = base + c + '/page/' + str(p)
        print(url)
        soup = BeautifulSoup(scraper.get(url).text)
        for i in soup.find_all('div', {'class' : 'category__card__text'}):
            direct_URLs.append(i.find('a')['href'])
        print('Now scraped ', len(direct_URLs), 'articles from this page ... ')

        final_result = direct_URLs.copy()
        len_final_result += len(final_result)
        print('The total count of final result is: ', len(final_result))


        for url in final_result:
            if url:
                print(url, "FINE")
                ## SCRAPING USING NEWSPLEASE:
                try:
                    soup = BeautifulSoup(scraper.get(url).text)
                    article = NewsPlease.from_html(scraper.get(url).text).__dict__

                    # add on some extras
                    article['date_download']=datetime.now()
                    article['download_via'] = "Direct2"
                    article['source_domain'] = source
                    article['url'] = url

                    # fix date
                    try:
                        date = soup.find('meta', property = 'article:published_time')['content']
                        article['date_publish'] = dateparser.parse(date).replace(tzinfo = None)

                    except:
                        try:
                            date = soup.find('time' , {'class' : 'post-published updated'})['datetime']
                            article['date_publish'] = dateparser.parse(date).replace(tzinfo = None)
                        except:
                            article['date_publish'] =article['date_publish'] 
                    print("newsplease date: ", article['date_publish'])

                    print("newsplease title: ", article['title'])
                    

                    try:
                        maintext = soup.find('div', {'class' : 'article__content'}).text
                        article['maintext'] = maintext.strip()
                    except:
                        maintext = ""
                        for i in soup.find('div', {'class' : 'article__content'}).find_all('p'):
                            maintext += i.text
                        article['maintext'] = maintext.strip()
                        
                    if article['maintext']:
                        print("newsplease maintext: ", article['maintext'][:50])
                    

                    try:
                        year = article['date_publish'].year
                        month = article['date_publish'].month
                        colname = f'articles-{year}-{month}'
                        #print(article)
                    except:
                        colname = 'articles-nodate'
                    # Inserting article into the db:
                    try:
                        db[colname].insert_one(article)
                        # count:
                        if colname != 'articles-nodate':
                            url_count = url_count + 1
                            print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        # db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        db[colname].delete_one({'url' : url})
                        db[colname].insert_one(article)
                        pass
                        print("DUPLICATE! Not inserted.")
                    
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
                processed_url_count += 1
                print('\n',processed_url_count, '/', len_final_result, 'articles have been processed ...\n')
        
            else:
                pass

        print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
        direct_URLs = []