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
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from dotenv import load_dotenv

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

source = 'metroecuador.com.ec'

direct_URLs = []

# collect new urls from sitemaps
year = [2024]
months = range(5, 6)
days = range(10, 32)
for y in year:
    y_str = str(y)
    for m in months:
        if m < 10:
            m_str = '0' + str(m)
        else:
            m_str = str(m)
        for d in days:
            if d < 10:
                d_str = '0' + str(d)
            else:
                d_str = str(d)
            link = 'https://www.metroecuador.com.ec/arc/outboundfeeds/sitemap/' + y_str + '-' + m_str + '-' + d_str + '/?outputType=xml'

            reqs = requests.get(link, headers=headers)
            soup = BeautifulSoup(reqs.text, 'html.parser')
            for i in soup.find_all('loc'):
                direct_URLs.append(i.text)
            print('Now scraped ', len(direct_URLs), 'articles from', y_str, m_str, d_str, 'sitemaps ... ')


blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

final_result = list(set(direct_URLs))

print('The total count of final result is: ', len(final_result))

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
            print("newsplease date: ", article['date_publish'])
            print("newsplease title: ", article['title'])
            
            try:
                maintext = ''
                soup.find('article', {'class' : 'default__ArticleBody'}).find_all('p', {'class' : 'default__StyledText'})
                for i in soup.find('article', {'class' : 'default__ArticleBody'}).find_all('p', {'class' : 'default__StyledText'}):
                    maintext += i.text
                article['maintext'] = maintext
            except:
                article['maintext'] = article['maintext']
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

                    