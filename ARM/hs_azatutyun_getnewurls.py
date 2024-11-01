
import requests
import io as io
from io import StringIO ## for Python 3
# Packages:
import random
import sys
sys.path.append('../')
import os
import re
#from p_tqdm import p_umap
#from tqdm import tqdm
from pymongo import MongoClient
import random
from urllib.parse import urlparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from pymongo.errors import CursorNotFound
import requests
#from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
#from dotenv import load_dotenv
from bs4 import BeautifulSoup
# %pip install dateparser
import dateparser
import pandas as pd


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'azatutyun.am'

### EXTRACTING ulrs from sitemaps:
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
# 'news', 
category = ['z/2039', 'z/2095', 'z/2041', 'z/2040', 'z/2038', 'z/2081', 'z/2037']
direct_URLs = []
for year in range(2023, 2024):
    for month in range(8, 9):
        for day in range(1, 32):
            for p in range(1, 8):
                for c in category:
                    url = 'https://www.azatutyun.am/' + c + '/' + str(year) + '/' + str(month) + '/' + str(day) + '?p=' + str(p)
                    print(url)
                    reqs = requests.get(url, headers=headers)
                    soup = BeautifulSoup(reqs.text, 'html.parser')

                    for i in soup.find_all('div', {'class' : 'media-block'}):
                        direct_URLs.append(i.find('a')['href'])
        print('Now collected', len(list(set(direct_URLs))), 'URLs ... ')

direct_URLs = list(set(direct_URLs))

direct_URLs = ['https://www.azatutyun.am' + i for i in direct_URLs]

final_result = direct_URLs.copy()

url_count = 0
processed_url_count = 0

for url in final_result:
    ## INSERTING IN THE DB:
    try:
        print(url)
        #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
        header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        response = requests.get(url, headers=header)
        # process
        article = NewsPlease.from_html(response.text, url=url).__dict__
        # add on some extras
        article['date_download']=datetime.now()
        article['download_via'] = "Direct_HS"
        article['source_domain'] = source
        article['language'] = 'hy'
        
        ## Fixing what needs to be fixed:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Get Title:
        try:
            contains_title = soup.find("meta", {"name":"title"})
            title = contains_title['content']
            article['title'] = title
        except:
            try:
                title = soup.find("title").text
                article['title'] = title
            except:
                article['title'] = article['title']

        print('Title: ', article['title'])


        # Get Main Text:
        if article['maintext'] == None:
            try:
                maintext = soup.find("div", {"class":"wsw"}).text
                article['maintext'] = maintext
            except:
                try:
                    contains_maintext = soup.find("meta", {"name":"description"})
                    maintext = contains_maintext['content']
                    article['maintext'] = maintext  
                except: 
                    maintext = None
                    article['maintext']  = None

        print('Maintext: ', article['maintext'][:50])

        
        ## Fixing Date:
        try:
            contains_date = soup.find("time")['datetime']
            article_date = dateparser.parse(contains_date)
            article['date_publish'] = article_date
        except:
            article['date_publish'] = article['date_publish'] 
            
        print('Date: ', article['date_publish'])
        ## Inserting into the db
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
            db['urls'].insert_one({'url': article['url']})
        except DuplicateKeyError:
            db[colname].delete_one({'url' : url})
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

