
# Packages:
import time
import random
import sys
sys.path.append('../')
import os
import re
from p_tqdm import p_umap
from tqdm import tqdm
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
from dotenv import load_dotenv
from bs4 import BeautifulSoup
# %pip install dateparser
import dateparser
import pandas as pd

# db connection:
uri = 'mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true'
db = MongoClient(uri).ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## NEED TO DEFINE SOURCE!
source = 'twala.info'

direct_URLs = []

for p in range(0, 30+1, 6):
    url = 'https://twala.info/fr/category/a-chaud-actualite-algerienne/?offset=' + str(p)

    print("Extracting from ", url)
    response = requests.get(url, verify=False)

    soup = BeautifulSoup(response.content)
    # 
    a_with_h4 = soup.find_all('a', recursive=True, text=False)
    a_with_h4 = [a for a in a_with_h4 if a.find('h4')]

    # Output the result
    for tag in a_with_h4:
        direct_URLs.append(tag['href'])
    print(len(direct_URLs))
final_result = direct_URLs.copy()
    
# for url in ['https://twala.info/fr/category/business/?offset=0', 'https://twala.info/fr/category/business/?offset=0']:
#     response = requests.get(url, verify=False)

#     soup = BeautifulSoup(response.content)
#     a_with_h4 = soup.find_all('a', recursive=True, text=False)
#     a_with_h4 = [a for a in a_with_h4 if a.find('h4')]

#     # Output the result
#     for tag in a_with_h4:
#         direct_URLs.append(tag['href'])
#     print(len(direct_URLs))
        
# for p in range(0, 170, 6):
#     url = 'https://twala.info/fr/cformat/fil_actualite/?offset=' + str(p)
#     response = requests.get(url, verify=False)

#     soup = BeautifulSoup(response.content)
#     for i in soup.find_all('h5'):
#         direct_URLs.append(i.find('a')['href'])
#     print(len(direct_URLs))
        
final_result = direct_URLs.copy()
print('Total number of urls found: ', len(final_result))


url_count = 0
processed_url_count = 0
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
            article['language'] = 'fr'
            # title has no problem
         
            soup = BeautifulSoup(response.content, 'html.parser')

            try:
                date = soup.find('meta', {'property' : 'indepth:published-date'})['content']
                article['date_publish'] = dateparser.parse(date)
            except:
                article['date_publish'] = article['date_publish']
            print("newsplease date: ", article['date_publish'])
            print("newsplease title: ", article['title'])

            try:
                maintext = soup.find('meta', {'property' : 'og:description'})['content']
                article['maintext'] = maintext.strip()
            except:
                maintext = soup.find('p', {'class' : 'my-4'}).text
                article['maintext'] = maintext.strip()
                
            if  article['maintext']:
                print("newsplease maintext: ", article['maintext'][:50])
                   
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'articles-{year}-{month}'
                article['primary_location'] = "DZA"
                
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
                # db[colname].delete_one({'url': url})
                # db[colname].insert_one(article)
                pass
                print("DUPLICATE! Pass.")
                
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
