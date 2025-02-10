#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 5, 2022

@author: Hanling

 
"""
# Packages:
# Packages:

import re
from pymongo import MongoClient
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime
from pymongo.errors import DuplicateKeyError
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
import cloudscraper
from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
from pymongo import MongoClient
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import cloudscraper
from pymongo import MongoClient
from datetime import datetime
from bs4 import BeautifulSoup
import dateparser
from pymongo.errors import DuplicateKeyError
import re
# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
#headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}
        
## COLLECTING URLS
direct_URLs = []
siteurls = []

## NEED TO DEFINE SOURCE!
source = 'herald.co.zw'
base = 'https://www.herald.co.zw/category/'
categories = ['national', 'business', 'africa', 'international', 'crime-and-courts']

page_start = [1, 1, 1, 1]
# page_end = [1,1,1,1]
page_end = [140,40,7,8, 40]


scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)

for c, p_s, p_e in zip(categories, page_start, page_end):
    for p in range(p_s, p_e + 1):
        url = base + c + '/page/' + str(p)
        print(url)
        soup = BeautifulSoup(scraper.get(url).text, 'html.parser')
        for h3 in soup.find_all('h3', {'class' : 'h4'}):
            direct_URLs.append(h3.find('a')['href']) 
        print("URLs so far: ",len(direct_URLs))

blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

final_result = list(set(direct_URLs))
print('Total number of urls found for ', source, ': ', len(final_result))



## INSERTING IN THE DB:
url_count = 0
processed_url_count = 0
for url in final_result:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if 'herald.co.zw' in url:
                print(url, "FINE")
                ## SCRAPING USING NEWSPLEASE:
                try:
                    #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
                    #header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}
                    response = scraper.get(url)
                    # process
                    article = NewsPlease.from_html(response.text, url=url).__dict__
                    # add on some extras
                    article['date_download']= datetime.now()
                    article['download_via'] = "Direct2"
                    article['source_domain'] = 'herald.co.zw'


                    ## Fixing main text:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    try:
                        maintext = ''
                        soup.find('div', {'class' :'article-content'}).find_all('p')
                        for i in soup.find('div', {'class' :'article-content'}).find_all('p'):
                            if not i.find('strong'):
                                maintext+=i.text
                        article['maintext'] = maintext.strip()
                    except:
                        article['maintext'] = article['maintext']
                    print("newsplease maintext: ", article['maintext'][:100])
                    # fix title:
                    try:
                        title = soup.find('meta', property="og:title")['content']
                        article['title'] = title.strip()
                    except:
                        article['title'] = soup.find('div', {'class' : 'title'}).text
                        article['title'] = title.strip()

                    print("newsplease title: ", article['title'])

                    # fix date:
                    try:                 
                        article_date = soup.find("time", {"class":"hide-microdata published"}).text
                        article_date = dateparser.parse(article_date)
                        article['date_publish'] = article_date  
                
                    except:
                        pass
                    print("newsplease date: ", article['date_publish'])


                    ## Inserting into the db
                    try:
                        year = article['date_publish'].year
                        month = article['date_publish'].month
                        colname = f'articles-{year}-{month}'
                        #print(article)
                    except:
                        colname = 'articles-nodate'
                    try:
                        # Inserting article into the db:
                        db[colname].insert_one(article)
                        # count:
                        url_count = url_count + 1
                        # print("+ Date: ", article['date_publish'])
                        # print("+ Title: ", article['title'][0:50])
                        # print("+ Text: ", article['maintext'][0:200])
                        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        db[colname].delete_one({'url' : url})
                        db[colname].insert_one(article)
                        print("DUPLICATE! Updated.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
                processed_url_count += 1
                print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

            else:
                pass


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")