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
import re
import pandas as pd

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'koha.mk'

direct_URLs = []
base = 'https://www.koha.mk/post-sitemap'
hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

for p in range(216, 222):
    url = base + str(p) +'.xml'
    req = requests.get(url, headers = hdr)
    soup = BeautifulSoup(req.content)
    for i in soup.find_all('loc'):
        direct_URLs.append(i.text)
    print('Now collected ', len(direct_URLs), 'URLs...')

# direct_URLs= pd.read_csv('Downloads/peace-machine/peacemachine/getnewurls/MKD/kohamk.csv')['0']
final_result = direct_URLs.copy()

print(len(final_result))

url_count = 0
processed_url_count = 0

error_urls = []
for url in final_result[::-1]:
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
            
            try:
                category = soup.find('div', {'class' : 'tdb-category td-fix-index'}).text
            except:
                category = "news"
            
            print(category)
            
            if category in ['Kulturë', 'Sport', 'Tech', 'Kuriozitete', 'Infrared', 'Dossier', 'survey', 'Photo Gallery', 'Report']:
                article['date_publish'] = None
                article['maintext'] = None
                article['title'] = 'From uninterested category'
                print(article['title'], category)
            else:

                if not article['maintext']:
                    try:
                        maintext = ''
                        soup.find('div', {'class' : 'td_block_wrap tdb_single_content tdi_64 td-pb-border-top td_block_template_1 td-post-content tagdiv-type'}).find_all('p')
                        for i in soup.find('div', {'class' : 'td_block_wrap tdb_single_content tdi_64 td-pb-border-top td_block_template_1 td-post-content tagdiv-type'}).find_all('p'):
                            maintext += i.text
                        article['maintext'] = maintext.strip()

                    except:
                        try:
                            maintext = ''
                            items = soup.find('div', {'itemprop' : 'articleBody'}).find_all('p')
                            for i in items:
                                maintext += i.text
                            article['maintext'] = maintext.strip()
                        except:
                            try:
                                maintext = ''
                                soup.find('div', {'class' : 'entry-content rbct clearfix is-highlight-shares'}).find_all('p')
                                for i in soup.find('div', {'class' : 'entry-content rbct clearfix is-highlight-shares'}).find_all('p'):
                                    maintext += i.text
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
            error_urls.append(url)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')
 
    else:
        pass

error_urls_df = pd.DataFrame(error_urls)
error_urls_df.to_csv('/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/MKD/kohamk_error_urls6.csv')
print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
