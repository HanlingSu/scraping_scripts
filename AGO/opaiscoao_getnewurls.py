# Packages:
import sys
import os
import re
import getpass
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np 
from tqdm import tqdm

from pymongo import MongoClient


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
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from dotenv import load_dotenv

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'opais.co.ao'

documents = db.sources.find({'source_domain': source}, { 'source_domain':1, 'primary_location': 1, '_id': 0 })
for document in documents:
    primary_location = document['primary_location']

# direct_URLs = list(pd.read_csv('Downloads/peace-machine/peacemachine/getnewurls/AGO/opaiscoao.csv', names = ['url'])['url'])

# direct_URLs = [i.strip() for i in direct_URLs]


# final_result = list(pd.read_csv('Downloads/peace-machine/peacemachine/getnewurls/AGO/opaiscoao.csv')['Unnamed: 0'])

base = 'https://www.opais.ao/categoria/'

category = ['politica', 'sociedade', 'economia', 'mundo', 'opiniao']
cate_num = ['/?_gl=1%2A1kp1chp%2A_up%2AMQ..%2A_ga%2AMjA2Mjg4MDUzOS4xNzEyODU4Mjgw%2A_ga_VBLS1N932S%2AMTcxMjg1ODI3OS4xLjEuMTcxMjg1ODMwNC4wLjAuMA..', \
            '/?_gl=1%2A1tsl7bm%2A_up%2AMQ..%2A_ga%2AMjA2Mjg4MDUzOS4xNzEyODU4Mjgw%2A_ga_VBLS1N932S%2AMTcxMjg2MDc4Ny4yLjAuMTcxMjg2MDc4Ny4wLjAuMA..', \
            '/?_gl=1*8dnfsq*_up*MQ..*_ga*MjA2Mjg4MDUzOS4xNzEyODU4Mjgw*_ga_VBLS1N932S*MTcxMjg2MDc4Ny4yLjEuMTcxMjg2MDc5Ny4wLjAuMA..', \
            '/?_gl=1%2A13o5s9e%2A_up%2AMQ..%2A_ga%2AMjA2Mjg4MDUzOS4xNzEyODU4Mjgw%2A_ga_VBLS1N932S%2AMTcxMjg2MDc4Ny4yLjEuMTcxMjg2MTA1MS4wLjAuMA..', \
            '']
            
page_start = [1, 15, 1, 1, 10]
page_end = [0,50,30,35, 30]
url_count = 0
processed_url_count = 0
len_final_result = 0
for c, cn, ps, pe in zip(category, cate_num, page_start, page_end):
    direct_URLs = []
    print(c)
    for p in range(ps, pe+1):
        url = base + c + '/page/' + str(p) + cn
        print(url)
        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
        req = requests.get(url, headers = hdr)
        soup = BeautifulSoup(req.content)
        item = soup.find_all('h3')
        for i in item:
            try:
                link = i.find('a')['href']
                direct_URLs.append(link)
            except:
                pass
        print(len(direct_URLs))

    final_result = direct_URLs.copy()

    len_final_result += len(final_result)
    for url in final_result:
        if url:
            print(url, "FINE")
            ## SCRAPING USING NEWSPLEASE:
            try:
                #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
                header = hdr = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(url, headers=header)
                # process
                article = NewsPlease.from_html(response.text, url=url).__dict__
                # add on some extras
                article['date_download']=datetime.now()
                article['download_via'] = "Direct2"
                article['source_domain'] = source
                # title has no problem
                print("newsplease title: ", article['title'])
                
                # custom parser
                soup = BeautifulSoup(response.content, 'html.parser')
                
            
            
                try:
                    date = json.loads(soup.find_all('script', {'type' : 'application/ld+json'})[2].contents[0])['datePublished'][:19]
                    article['date_publish'] = dateparser.parse(date)
                except:
                    article['date_publish'] = None
                print("newsplease date: ",  article['date_publish'])

            
                print("newsplease maintext: ", article['maintext'][:50])
                
                
                try:
                    year = article['date_publish'].year
                    month = article['date_publish'].month
                    if  '/opiniao/' in url:
                        colname = f'opinion-articles-{year}-{month}'
                        article['primary_location'] = primary_location

                    else:
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
                    
            except Exception as err: 
                print("ERRORRRR......", err)
                pass
            processed_url_count += 1
            print('\n',processed_url_count, '/',len_final_result , 'articles have been processed ...\n')
    
        else:
            pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
