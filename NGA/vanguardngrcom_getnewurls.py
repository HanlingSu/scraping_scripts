# Packages:
import pymongo 
from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import cloudscraper
import pandas as pd
from tqdm import tqdm
import re
import sys
import json
import time
    

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

source = 'vanguardngr.com'


scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)

direct_URLs = []

categories = ['national-news', 'politics',  'columns/nigeria-today', 'columns/people-politics', 'metro', 'editorial']

base = 'https://www.vanguardngr.com/category/'


page_start = [1, 1, 1, 1, 1, 1]
page_end = [1, 1, 1, 1, 1, 1]

for c, ps, pe in zip(categories, page_start, page_end):
    for p in range(ps, pe +1):
        url = base + c + '/page/' + str(p)
        print(url)
        soup = BeautifulSoup(scraper.get(url).text)
        for i in soup.find_all('h3', {'class' : 'entry-title'}):
            direct_URLs.append(i.find('a')['href'])
        print('Now scraped ', len(direct_URLs), 'articles from previous months ... ')
        
           
print('There are ', len(direct_URLs), 'articles')


# delete blacklist URLs

final_result = direct_URLs.copy()


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
            article = NewsPlease.from_html(scraper.get(url).text, url=url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
 
            soup = BeautifulSoup(scraper.get(url).text)
            try:
                category = soup.find('div', {'class' : 'breadcrumbs-list-wrapper'}).find_all('a')[-1].text
            except:
                category = 'News'
            print(category)

            if category in ['Sports', 'Entertainment', 'Technology', 'Money Market', 'Capital Market', 'Insurance and You', \
            'Energy', 'Maritime Report', 'Money Digest', 'Article of Faith', 'Rational Perspectives', 'Talking Point', 'The Hub', \
            'Sweet and Sour', 'Sunday Perspectives', 'My World', 'Frankly Speaking', 'The Orbit', 'Vista Woman']:
                article['date_publish'] = None
                article['title'] = "From uninterested category"
                article['maintext'] = None
                print(article['title'], category)

            else:
                print("newsplease date: ", article['date_publish'])
                print("newsplease title: ", article['title'])

                
                try:
                    maintext = ''
                    for i in soup.find('div', {'class' : 'entry-content-inner-wrapper'}).find_all('p')[1:]:
                        maintext += i.text
                    article['maintext'] = maintext
                except:
                    article['maintext'] = article['maintext']
                    
                if article['maintext']:
                    print("newsplease maintext: ", article['maintext'][:50])
                    

            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                if category == 'Editorial':
                    colname = f'opinion-articles-{year}-{month}'
                    article['primary_location'] = "NGA"
                else:
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
                myquery = { "url": url, "source_domain" : source}
                db[colname].delete_one(myquery)
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
