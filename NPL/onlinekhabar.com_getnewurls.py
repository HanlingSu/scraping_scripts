# Packages:
import sys
import os
import re
import getpass
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np 
from pymongo import MongoClient
import bs4
from bs4 import BeautifulSoup
from newspaper import Article
from dateparser.search import search_dates
import dateparser
import requests
import urllib.request
from warnings import warn
import json
from pymongo import MongoClient
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from pymongo.errors import CursorNotFound
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []
base = 'https://www.onlinekhabar.com/content/news/rastiya/page/'
source = 'onlinekhabar.com'
#3995
for p in range(1, 40):
    sitemap = base + str(p) 
    print(sitemap)
    hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
    req = requests.get(sitemap, headers = hdr)
    soup = BeautifulSoup(req.content)
    item = soup.find_all('div',{'class':'span-4'})
    for i in item:
        url = i.find('div',{'class' : 'ok-news-post'}).find('a')['href']
        direct_URLs.append(url)

    print(len(direct_URLs))

# dfa = pd.DataFrame()
# for year in range(2023, 2024):
#     for month in range(8, 9):  
#         year_month = str(year)+'-'+str(month)
#         source_domain = ['onlinekhabar.com']
#         d1 = [i for i in db['articles-'+year_month].find({
#             # 'maintext':None,  
#             # 'maintext_translated': {'$exists':False},
#             'source_domain' : {'$in':  source_domain},})]
#         df1 = pd.DataFrame(d1)
#         dfa = dfa.append(df1)

# direct_URLs = dfa['url']
final_result = direct_URLs.copy()

url_count = 0
processed_url_count = 0


for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            # header = hdr = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=header)
            # process
            article = NewsPlease.from_html(response.content, url=url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            # title has no problem
            
            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
           
            article['language'] = 'ne'
            
        
            try:
                title = soup.find('meta', property="og:title")['content']
                article['title'] = title
            except:
                try:
                    title = soup.find('h1', {'class' :'entry-title'}).text
                    article['title'] = title
                except:
                    try:
                        title = soup.find('h2').text
                        article['title'] = title
                    except:
                        article['title'] = article['title'] 
            print("newsplease title: ", article['title'])

            try:
                maintext = ''
                for i in soup.find('div', {'class' : 'ok18-single-post-content-wrap'}).find_all('p'):
                    maintext += i.text.strip()
                article['maintext'] = maintext.strip()
            except:
                maintext = ''
                for i in soup.find('div', {'class' : 'okv4-post-single-page article-single-read pt-0 m-pl-20 m-pr-20'}).find_all('p'):
                    maintext += i.text.strip()

                article['maintext'] = maintext.strip()
            print("newsplease maintext: ", article['maintext'][:50])

            if not article['date_publish']:
                    date = url.replace('https://www.onlinekhabar.com/', '').split('/')
                    year= date[0]
                    month = date[1]
                    day = '01'
                    date = [year, month, day]
                    date = '-'.join(date)
                    article['date_publish'] = dateparser.parse(date, date_formats=['%Y %m %d'])
            print("newsplease date: ",  article['date_publish'])
            
            
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
                db[colname].delete_one({'url': url})
                db[colname].insert_one(article)

                pass
                print("DUPLICATE! Updated.")
                
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')
 
    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
