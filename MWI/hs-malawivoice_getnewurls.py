

"""
Created on Oct 24, 2022 

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

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'malawivoice.com'

direct_URLs = []
sitemap_base = 'https://www.malawivoice.com/post-sitemap'
for i in range(12, 13+1):
    
    sitemap = sitemap_base + str(i) +'.xml'
    print('Now scraping: ', sitemap)
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = requests.get(sitemap, headers = hdr)
    soup = BeautifulSoup(req.content)
    for link in soup.find_all('loc'):
        direct_URLs.append(link.text)
    print('Now have collected', len(direct_URLs), 'URLs ... ')


final_result = direct_URLs.copy()[::-1]

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
                category = [] 
                for i in soup.find_all('a', {'class' : 'tdb-entry-category'}):
                    category.append(i.text)
            except:
                category = ['News'] 
            
            blacklist = ['Entertainment', 'Sports']
            
            if any(x in blacklist for x in category):
                article['date_publish'] = None
                article['maintext'] = None
                article['title'] = "From uninterested category: " + category[-1]
                print(article['title'])
            else:
                    
                print('From category:', category)
                print("newsplease date: ", article['date_publish'])
                print("newsplease title: ", article['title'])
                if 'by' in article['maintext'][:3].lower():
                    article['maintext'] = article['maintext'].split('\n', 1)[1].strip()
                print("newsplease maintext: ", article['maintext'][:50])


    
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                if any(x in ['Opinion'] for x in category): 
                    colname = f'opinion-articles-{year}-{month}'
                    article['primary_location'] = "MWI"
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
                # db[colname].delete_one({ "url": url, "source_domain" : source})
                # db[colname].insert_one(article)
                # print("DUPLICATE! Updated.")
                pass
                
                print("DUPLICATE! pass.")
                
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        # print('\nNow scraping ', sitemap)
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
