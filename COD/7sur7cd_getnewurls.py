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
sitemap_base = 'https://7sur7.cd/sitemap.xml?page='
source = '7sur7.cd'

for p in range(32, 34):
    sitemap = sitemap_base + str(p) + '.xml'
    hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    req = requests.get(sitemap, headers = hdr)
    soup = BeautifulSoup(req.content)
    item = soup.find_all('loc')
    for i in item:
        direct_URLs.append(i.text)

    print('Now scraped ', len(direct_URLs), ' articles from previous sitemaps.')


final_result = list(set(direct_URLs))   
print('Total number of urls found: ', len(final_result))



url_count = 0
processed_url_count = 0

for url in final_result:
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
            # title has no problem
            # print(soup)
            try:
                category = soup.find('meta', {'property' : 'article:section'})['content']
            except:
                category = 'News'
            
            if category in ['Sport', 'Culture']:
                print("From uninterested category: ", category)
            
            else:
                try:
                    title = soup.find('meta', {'property': 'og:title'})['content']
                    article['title'] = title
                except:
                    title = soup.find('h1', {'class' : 'page-header'}).text
                    article['title'] = title

                print("newsplease title: ", article['title'])
                if not article['maintext']:
                    try:
                        maintext = ''
                        for i in soup.find_all('p', {'class' : None}):
                            maintext += i.text
                        article['maintext'] = maintext.strip()
                    except:
                        pass

                if article['maintext']:
                    print("newsplease maintext: ", article['maintext'][:50])
                
                try:
                    date = soup.find('meta', {'property' : 'article:published_time'})['content']
                    article['date_publish'] = dateparser.parse(date)
                except:
                    date = soup.find('div', {'class' : 'views-field views-field-created'}).text
                    article['date_publish'] = dateparser.parse(date)
                print("newsplease date: ",  article['date_publish'])



            if category not in  ['Sport', 'Culture']:
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
