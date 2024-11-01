"""
Created on July 22 2022

@author: serkantadiguzel

This script scrapes/updates 'firstpost.com' using sitemaps. 

The sitemaps are found for each month, so we just need to get the new months as we update this source.
""" 
 
import random
import sys
import os
import re
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from pymongo.errors import CursorNotFound
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date, timedelta
from newsplease import NewsPlease
from datetime import datetime
import dateparser
import time


db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p




headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

source = 'firstpost.com'


baseurl = 'https://www.firstpost.com/feeds/sitemap/sitemap-pt-post-'

#months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
months = [ 11]
#years = [2016, 2017]
#years = [2018, 2019]
years = [2022]

#https://www.firstpost.com/feeds/sitemap/sitemap-pt-post-2018-09.xml
links = []
for year in years:
    for month in months:
        year_month = str(year) + '-' + str(month).zfill(2)
        sitemapurl = baseurl + year_month + '.xml'
        print(sitemapurl)
        reqs = requests.get(sitemapurl, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')
        for link in soup.find_all('loc'):
            links.append(link.text)


  
blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
links = [word for word in links if not blacklist.search(word)]

clean_links = list(set(links))
print('Clean links:', len(clean_links))




## INSERTING IN THE DB:
url_count = 0
progress_count = 0
for url in cleaner_links:

    if url == "":
        continue
    else:
        if url == None:
            continue
    print(url)
    try:
        response = requests.get(url, headers=headers)
    except:
        time.sleep(0.5)
        try:
            response = requests.get(url, headers=headers)
        except:
            continue

    try:    
        article = NewsPlease.from_html(response.text).__dict__
        soup = BeautifulSoup(response.text, 'html.parser')
    except ValueError:
        continue




    try:
        date = soup.find('meta', property = 'article:published_time')['content']
        article['date_publish'] = dateparser.parse(date).replace(tzinfo = None)
    except:
        try:
            correct_date_list = soup.find('div', {'class' : 'author-info'}).text.strip().split('\n')
            correct_date = correct_date_list[len(correct_date_list)-1].strip()
            correct_date_final = dateparser.parse(correct_date,settings={'RETURN_AS_TIMEZONE_AWARE': False})
            article['date_publish'] = correct_date_final

        except:
            try:
                correct_date = soup.find('span', {'class' : 'post-date'}).text.strip()
                correct_date_final = dateparser.parse(correct_date,settings={'RETURN_AS_TIMEZONE_AWARE': False})
                article['date_publish'] = correct_date_final

            except:

                article['date_publish'] = article['date_publish'] 


    print('Date extracted:', article['date_publish'])

    # add on some extras
    article['date_download']=datetime.now()
    article['download_via'] = "Direct2" #change
    article['source_domain'] = source

    # add a fix: highlighted section is in the description so we can add that part to the maintext too
    try:
        article['maintext'] = article['description'] + ' ' + article['maintext']
    except:
        pass
    if article['maintext']:
        print(article['maintext'][:50])

    ## Inserting into the db
    try:
        year = article['date_publish'].year
        month = article['date_publish'].month
        colname = f'articles-{year}-{month}'
        #print(article)
    except:
        colname = 'articles-nodate'

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


    progress_count += 1
    print('\n',progress_count, '/', len(cleaner_links), 'articles have been processed ...\n')




print("Done inserting ", url_count, "collected urls from ",  source, " into the db.")

