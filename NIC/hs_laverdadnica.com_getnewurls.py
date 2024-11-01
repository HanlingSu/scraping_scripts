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

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem


software_names = [SoftwareName.ANDROID.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value, OperatingSystem.MAC.value]   

user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=1000)

# Get list of user agents.
user_agents = user_agent_rotator.get_user_agents()[0]['user_agent']
print(user_agents)

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

headers = {'User-Agent': user_agents}
 
source = 'laverdadnica.com'

direct_URLs = []

base = 'https://laverdadnica.com/'

# page_start = 1
# page_end = 100
# for p in range(page_start, page_end +1):
#     url = base + str(p)
#     reqs = requests.get(url, headers=headers)
#     soup = BeautifulSoup(reqs.text, 'html.parser')
#     for i in soup.find_all('h3', {'class' : 'entry-title td-module-title'}):
#         direct_URLs.append(i.find('a')['href'])
#     print('Now scraped ', len(direct_URLs), 'articles from previous pages ... ')
        
header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}

category = ['politica', 'internacionales',  'nacionales', 'monitoreo-nacional', 'sucesos', 'noticias-departamentales']
page_start = [1, 1, 1, 1, 1, 1]
page_end = [1, 1, 1, 1, 1, 1]

for c, ps, pe in zip(category, page_start, page_end):
    for p in range(ps, pe+1):
        url = base + c + '/' + str(p)
        print(url)
        reqs = requests.get(url, headers=header)
        soup = BeautifulSoup(reqs.text, 'html.parser')
        for i in soup.find_all('h3', {'class' : 'elementor-post__title'}):
            direct_URLs.append(i.find('a')['href'])
        print('Now scraped ', len(direct_URLs), 'articles from previous pages ... ')
    # print(direct_URLs)


# delete blacklist URLs
# blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
# blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
# direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

final_result = list(set(direct_URLs))


print('The total count of final result is: ', len(final_result))

url_count = 0
processed_url_count = 0
for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            # header = {'User-Agent': user_agents}
            response = requests.get(url, headers=header)
            # process
            article = NewsPlease.from_html(response.text, url=url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            print("newsplease date: ", article['date_publish'])
            print("newsplease title: ", article['title'])
            
            soup = BeautifulSoup(response.text, 'html.parser')
        
            # Get Main Text:

            if  article['maintext']:
                article['maintext'] = article['maintext'].split('\n', 4)[4]
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
                # myquery = { "url": url, "source_domain" : source}
                # db[colname].delete_one(myquery)
                # db[colname].insert_one(article)
                print("DUPLICATE! Pass.")
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')
   
    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
