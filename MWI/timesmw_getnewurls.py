"""
Created on Oct 25, 2022 

Craated by Hanling Su
"""

# Packages:

from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from datetime import datetime
from pymongo.errors import DuplicateKeyError
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
import re
import pandas as pd

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'times.mw'
hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# final_result = list(pd.read_csv('Downloads/peace-machine/peacemachine/getnewurls/MWI/timesmw.csv')['0'])
# print(len(final_result))
# direct_URLs = []
# url = 'https://times.mw/wp-sitemap-posts-post-1.xml'
# req = requests.get(url, headers = hdr)
# soup = BeautifulSoup(req.content)

# for i in soup.find_all('loc'):
#     direct_URLs.append(i.text)

# final_result = direct_URLs.copy()


direct_URLs = []

sections  = ['national', 'world', 'business-2', ]
page_start = [1, 1, 1 ]
page_end = [40, 6, 30]

base = 'https://times.mw/category/'
for s, ps, pe in zip(sections, page_start, page_end):
    for p in range(ps, pe+1):
        url = base + s +'/page/' +str(p)
        print(url)
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = requests.get(url, headers = hdr)
        soup = BeautifulSoup(req.content)
        for link in soup.find_all('h3', {'class' : 'entry-title'}):
            direct_URLs.append(link.find('a')['href'])
        print('Now collected',len(direct_URLs), 'URLs')

final_result = list(set(direct_URLs))
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

            # blacklist by category
            soup = BeautifulSoup(response.content, 'html.parser')

            try: 
                category = soup.find('div', {'class' : 'p-categories'}).text.strip()
            except:
                category = 'News'
            
            
            if category in ['Entertainment', 'Sports']:
                article['date_publish'] = None
                article['maintext'] = None
                article['title'] = "From uninterested category: " + category
                print(article['title'])
            else:
                print('From category:', category)

                # fix maintext
                # maintext = ''
                # for i in soup.find('div', {'class' :'entry-content entry clearfix'}).find_all('p'):
                #     maintext += i.text
                # article['maintext'] = maintext.strip()
    
                print("newsplease date: ", article['date_publish'])
                print("newsplease title: ", article['title'])
                if 'by' in article['maintext'][:3].lower():
                    article['maintext'] = article['maintext'].split('\n', 1)[1].strip()
                print("newsplease maintext: ", article['maintext'][:50])

      
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

                pass
                print("DUPLICATE! Not inserted.")
                
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
