# Packages:

import re
from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests

from pymongo import MongoClient
from urllib.parse import urlparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from pymongo.errors import CursorNotFound
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []
sitemap_base = 'https://mzalendo.co.tz/post-sitemap'
source = 'mzalendo.co.tz'

for p in range(11, 12):
    sitemap = sitemap_base + str(p) + '.xml'
    hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    req = requests.get(sitemap, headers = hdr)
    soup = BeautifulSoup(req.content)
    item = soup.find_all('loc')
    for i in item:
        direct_URLs.append(i.text)

    print('Now scraped ', len(direct_URLs), ' articles from previous sitemaps.')


final_result = direct_URLs.copy()
print('Total number of urls found: ', len(final_result))



url_count = 0
processed_url_count = 0

for url in final_result[::-1]:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}

            response = requests.get(url, headers=hdr)
            # process
            soup = BeautifulSoup(response.content)

            article = NewsPlease.from_html(response.text, url=url).__dict__

            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            article['language'] = 'sw'
            # title has no problem
            # print(soup)
          
            print("newsplease title: ", article['title'])

            if not article['maintext']:
                try:
                    maintext = soup.find('div', {'class' : 'entry-content'}).text
                    article['maintext'] = maintext.strip()
                except:
                    article['maintext'] =article['maintext'] 
            if article['maintext']:
                print("newsplease maintext: ", article['maintext'][:50])
            
            print("newsplease date: ",  article['date_publish'])



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
