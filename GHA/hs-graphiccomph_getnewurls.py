#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Aug 24 2022

@author: hanling

This script updates graphic.com.gh -- it must be edited to 
scrape the most recent articles published by the source.

It needs to be run everytime we need to update GHA sources. 
"""
# Packages:
from pymongo import MongoClient
from bs4 import BeautifulSoup
from dateparser.search import search_dates
import dateparser
import requests
from urllib.parse import quote_plus
import time
from datetime import datetime
from pymongo.errors import DuplicateKeyError
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from dotenv import load_dotenv
import re
import cloudscraper

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

direct_URLs = []

###################################
# edit sitemap ending number here #
###################################``
source = 'graphic.com.gh'
base = 'https://www.graphic.com.gh/'

categories = ['news/general-news', 'news/politics', 'international/international-news', ]
page_start = [0, 0, 0]
# page_start = [2000, 600, 200]
page_end = [2000, 700, 330]
for c, ps, pe in zip(categories, page_start, page_end):
    for p in range(ps, pe+1, 1):
        url = base + c + '.html?start=' + str(p) 
        print(url)
        soup = BeautifulSoup(scraper.get(url).text)
        # print('Now scraping ', url)

        # for general-news
        if c == 'news/general-news':
            for i in soup.find_all('h2'):

            # for politics and international news
            # for i in soup.find_all('td', {'class' : 'list-title'}):
                try:
                    direct_URLs.append(i.find('a')['href'])
                except:
                    pass
        else:
            # for politics and international news
            for i in soup.find_all('td', {'class' : 'list-title'}):
                try:
                    direct_URLs.append(i.find('a')['href'])
                except:
                    pass
        print(len(direct_URLs))


blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

direct_URLs = ['https://www.graphic.com.gh' + i  for i in direct_URLs if 'https://www.graphic.com.gh'  not in i]
final_result = list(set(direct_URLs))


print("Total number of urls found: ", len(final_result))

# insert news articles
url_count = 0
processed_url_count = 0
for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
#             response = requests.get(url, headers=header)
            # process
            article = NewsPlease.from_html(scraper.get(url).text, url=url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            # title has no problem
            print("newsplease title: ", article['title'])
            # print("newsplease date: ",  article['date_publish'])
            
            # custom parser
            ## Fixing Date:
            soup = BeautifulSoup(scraper.get(url).text)
            try:
                contains_date = soup.find("time")
                contains_date = contains_date["datetime"]
                article_date = dateparser.parse(contains_date, date_formats=['%d/%m/%Y']).replace(tzinfo = None)
                article['date_publish'] = article_date
            except:
                article_date = article['date_publish']
                article['date_publish'] = article_date
            print("newsplease date: ",  article['date_publish'])

    # fix main text
            try:
                soup.find('div', {'class' : 'article-details'}).find_all('p')
                maintext = ''
                for i in soup.find('div', {'class' : 'article-details'}).find_all('p'):
                    maintext+=i.text

                article['maintext'] = maintext.strip()
            except:
                article['maintext'] = article['maintext']
            if article['maintext']:
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
                db[colname].delete_one({'url' : url})
                db[colname].insert_one(article)
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
