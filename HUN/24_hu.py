"""
Created on July 22 2022

@author: serkantadiguzel

This script scrapes/updates '24.hu' using sitemaps. 

Sitemaps are indexed from 1 to 94 [at the time of writing, September 20, 2022], so one can loop through the months to collect urls from the desired sitemaps. Smaller numbered sitemaps are newer articles, so the next updates should probably focus only on the first couple of sitemaps.


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

source = '24.hu'



baseurl = 'https://24.hu/app/uploads/sitemap/24.hu_sitemap_'
links = []
for i in range(1, 2): ## UPDATE
    sitemapurl = baseurl + str(i) + '.xml'
    print(sitemapurl)
    reqs = requests.get(sitemapurl, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    for link in soup.find_all('loc'):
        links.append(link.text)



# links = list(set(links))
print('TOTAL LINKS:', len(links))

## INSERTING IN THE DB:
url_count = 0
for url in links[8000:]:
    if url == "":
        continue
    else:
        if url == None:
            continue
    
    try:
        article = NewsPlease.from_url(url).__dict__
    except:
        time.sleep(0.5)
        try:
            article = NewsPlease.from_url(url).__dict__
        except:
            continue  

       
    # add on some extras
    article['date_download']=datetime.now()
    article['download_via'] = "Direct2" #change
    article['source_domain'] = source


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

        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
    except DuplicateKeyError:
        print("DUPLICATE! Not inserted.")




print("Done inserting ", url_count, "collected urls from ",  source, " into the db.")