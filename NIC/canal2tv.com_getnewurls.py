
# Packages:
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
import cloudscraper
import pandas as pd

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'canal2tv.com'

### EXTRACTING ulrs from sitemaps:

direct_URLs = []
hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# post-sitemap 
for j in range(22,24):
    url = 'https://canal2tv.com/post-sitemap' + str(j) + '.xml'

    print("Sitemap: ", url)
    response = requests.get(url, headers=hdr)
    soup = BeautifulSoup(response.content)
    for link in soup.findAll('loc'):
        direct_URLs.append(link.text)

    print(len(direct_URLs))


# STEP 1: Get rid or urls from blacklisted sources

blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

final_result = direct_URLs.copy()



print("Total number of USABLE urls found: ", len(final_result))



## INSERTING IN THE DB:
url_count = 0
processed_url_count = 0
for url in final_result[::-1]:

    print(url, "FINE")
    ## SCRAPING USING NEWSPLEASE:
    try:
        #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
        response = requests.get(url, headers=hdr)
        # process
        soup = BeautifulSoup(response.content)

        # process
        article = NewsPlease.from_html(response.text, url=url).__dict__

        # add on some extras
        article['date_download']=datetime.now()
        article['download_via'] = "Direct2"
        article['source_domain'] = source
        if not article['maintext']:
            try:
                maintext = soup.find('meta', {'property' : 'og:description'})['content']
                article['maintext'] = maintext
            except:
                article['maintext'] = article['title']
        print('newsplease maintext', article['maintext'][:50])
        print('newsplease title', article['title'])
        print('newsplease date', article['date_publish'])

        ## Fixing what needs to be fixed:
        soup = BeautifulSoup(response.content, 'html.parser')

        ## Inserting into the db
        try:
            year = article['date_publish'].year
            month = article['date_publish'].month
            colname = f'articles-{year}-{month}'
            #print(article)
        except:
            colname = 'articles-nodate'
        try:
            #TEMP: deleting the stuff i included with the wrong domain:
            #myquery = { "url": final_url, "source_domain" : 'web.archive.org'}
            #db[colname].delete_one(myquery)
        
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

 
print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")