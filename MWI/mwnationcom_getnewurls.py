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

source = 'mwnation.com'

# direct_URLs = []

# sitemap_base = 'https://mwnation.com/post-sitemap'
# for i in range(81, 83):
#     direct_URLs = []
#     sitemap = sitemap_base + str(i) +'.xml'
#     print('Now scraping: ', sitemap)
#     hdr = {'User-Agent': 'Mozilla/5.0'}
#     req = requests.get(sitemap, headers = hdr)
#     soup = BeautifulSoup(req.content)
#     for link in soup.find_all('loc'):
#         direct_URLs.append(link.text)
#     print('Now have collected', len(direct_URLs), 'URLs ... ')

direct_URLs = []

sections  = ['national-news', 'politics', 'society', 'columns', 'business/business-news']
page_start = [1, 1, 1 ,1, 1]
page_end = [80,1,1, 1, 22]

base = 'https://mwnation.com/category/'
for s, ps, pe in zip(sections, page_start, page_end):
    for p in range(ps, pe+1):
        url = base + s +'/page/' +str(p)
        print(url)
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = requests.get(url, headers = hdr)
        soup = BeautifulSoup(req.content)
        for link in soup.find_all('h2', {'class' : 'post-title'}):
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
                category = soup.find('div', {'id' : 'breadcrumbs'}).find_next('span').find_next('span').text.strip()
            except:
                category = 'News'
            
            
            if category in ['Entertainment', 'Life & Style', 'Sports']:
                article['date_publish'] = None
                article['maintext'] = None
                article['title'] = "From uninterested category: " + category
                print(article['title'])
            else:

                # fix maintext
                try:
                    maintext = ''
                    for i in soup.find('div', {'class' : 'content-inner'}).find_all('p'):
                        maintext += i.text
                    article['maintext'] = maintext.strip()
                except:
                    article['maintext'] = article['maintext'] 
                    
                print('From category:', category)
                print("newsplease date: ", article['date_publish'])
                print("newsplease title: ", article['title'])
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
