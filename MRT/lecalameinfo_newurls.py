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

categories = ['Chronique', 'Calamités', 'Interviews', 'Tribune', 'Actualit%C3%A9s', 'D%C3%A9bat%20/%20Courrier', 'Calamités'] 
                # news       releases,      editorial, interviews,        debate          chronicles
page_start = [0, 0, 0, 0, 0, 0, 0]

page_end = [2, 1, 2, 2, 16, 9, 1]


for c, ps, pe in zip(categories, page_start, page_end):
    direct_URLs = []
    print(c)
    for i in range( ps, pe+1):
        link = 'http://www.lecalame.info/?q=' + c + '&page=' + str(i)
        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
        try: 
            req = requests.get(link, headers = hdr)
            soup = BeautifulSoup(req.content)
            
            item = soup.find_all('div', {'class' : 'node node-content node-teaser clearfix'})
            for i in item:
                direct_URLs.append(i.find('a', href = True)['href'])
            print(len(direct_URLs))
        except:
            pass

    direct_URLs =list(set(direct_URLs))

    final_result = ['http://www.lecalame.info' + i for i in direct_URLs]

    print(len(final_result))

    url_count = 0
    processed_url_count = 0
    source = 'lecalame.info'
    for url in final_result:
        if url:
            print(url, "FINE")
            ## SCRAPING USING NEWSPLEASE:
            try:
                #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
                header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                response = requests.get(url, headers=header)
                # process
                article = NewsPlease.from_html(response.text, url=url).__dict__
                # add on some extras
                article['date_download']=datetime.now()
                article['download_via'] = "Direct2"
                article['source_domain'] = source
                #print("newsplease date: ", article['date_publish'])

                ## Fixing Date:
                soup = BeautifulSoup(response.content, 'html.parser')

            
                try:
                    article_date = soup.find('span', {'class' : 'date'}).text
                    article_date = dateparser.parse(article_date)
                    article['date_publish'] = article_date
                except:
                    article_date = None
                    article['date_publish'] = article_date
                if article['date_publish'] :
                    print('Date modified! ', article['date_publish'])
                    
                    
                ## Fixing Title:
                try:
                    article_title = soup.find("div", {"id":"title"}).text
                    article['title']  = article_title   
                except:
                    try:
                        article_title = soup.find("title").text.split('|')[0]
                        article['title']  = article_title  
                    except:
                        article_title  = None
                        article['title'] = article_title
                if article['title']:
                    print('Title modified! ', article['title'])
                    

                # Get Main Text:
                try: 
                    maintext = soup.find('article', {'class':"content clearfix"}).text
                    article['maintext'] = maintext
    
                except:
                    maintext = None
                    article['maintext'] = maintext
                if article['maintext']:
                    print('Main text modified! ', article['maintext'][:50])
                        

                try:
                    year = article['date_publish'].year
                    month = article['date_publish'].month
                    print(c)
                    if c == "Calamités":
                        colname = f'opinion-articles-{year}-{month}'
                        article['primary_location'] = "MRT"
                    else:
                        colname = f'articles-{year}-{month}'

                    #print(article)
                except:
                    colname = 'articles-nodate'
                #print("Collection: ", colname)
                try:
                    #TEMP: deleting the stuff i included with the wrong domain:
                    #myquery = { "url": final_url, "source_domain" : 'web.archive.org'}
                    #db[colname].delete_one(myquery)
                    # Inserting article into the db:
                    db[colname].insert_one(article)
                    # count:
                    if colname != 'articles-nodate':
                        url_count = url_count + 1
                        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                    else:
                        print("Inserted! in ", colname)
                    db['urls'].insert_one({'url': article['url']})

                except DuplicateKeyError:
                    print("DUPLICATE! Not inserted.")
            except Exception as err: 
                print("ERRORRRR......", err)
                pass
            processed_url_count += 1
            print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

        else:
            pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
