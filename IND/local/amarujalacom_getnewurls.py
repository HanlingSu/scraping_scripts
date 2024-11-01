"""
Created on Nov 3, 2022 

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
import json
import pandas as pd


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'amarujala.com'
sitemap_base = 'https://www.amarujala.com/sitemap/sitemap-'


final_count = 0
final_inserted_url_count =0

page_start = 268
page_end = 268
# 11701  262
for p in range(page_start, page_end+1):
    direct_URLs = []
    sitemap = sitemap_base + str(p)  + '.xml'
    hdr = {'User-Agent': 'Mozilla/5.0'} #header settings

    req = requests.get(sitemap, headers = hdr)
    soup = BeautifulSoup(req.content)

    for i in soup.find_all('loc'):
        direct_URLs.append(i.text)
    print('Now collected',len(direct_URLs), 'URLs')

    blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
    blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
    direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

    final_result = direct_URLs.copy()
    print('Total articles collected from current sitemap', len(final_result))
    final_count += len(final_result) 

    inserted_url_count = 0
    processed_url_count = 0

    for url in final_result:
        print(url)
        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
        try:
            req = requests.get(url, headers = hdr)
            soup = BeautifulSoup(req.content)
            article = NewsPlease.from_html(req.text, url=url).__dict__
            
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source

            print("newsplease title: ", article['title'])
            # fix date
    
            try:
                date = json.loads(soup.find_all('script', type = 'application/ld+json')[3].contents[0])['datePublished']
                article['date_publish'] = dateparser.parse(date).replace(tzinfo = None)
            except:
                try:
                    date = soup.find('div', {'class' : 'authdesc'}).text.split(',')[-1].strip()
                    article['date_publish'] = dateparser.parse(date).replace(tzinfo = None)
                except:
                    article['date_publish'] = article['date_publish'] 
                
            print("newsplease date: ", article['date_publish'])

            # fix maintext
            try:
                maintext = soup.find('div',{ "class" : 'article-desc ul_styling'}).text
                article['maintext'] = maintext.strip()
            except:
                try:
                    maintext = soup.find('div',{ "class" : 'auw_speak_body'}).text
                    article['maintext'] = maintext.strip()
                except:
                    article['maintext'] =article['maintext'] 
            if article['maintext']:
                print("newsplease maintext: ", article['maintext'][:50])

        except:
            continue
        
        # add to DB
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
                inserted_url_count += 1
                print("Inserted! in ", colname, " - number of urls so far: ", inserted_url_count)
            db['urls'].insert_one({'url': article['url']})
        except DuplicateKeyError:
            pass
            print("DUPLICATE! Not inserted.")
            
        processed_url_count +=1    
        print('\n',processed_url_count, '/', len(final_result) , 'articles from sitemap', str(p), ' have been processed ...\n')

    final_inserted_url_count += inserted_url_count
    

print("out of",final_count," urls, done inserting ", final_inserted_url_count, " from ",  source, " into the db.")
        



