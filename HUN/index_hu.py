"""
Created on July 22 2022

@author: serkantadiguzel

This script scrapes/updates 'index.hu' using sitemaps. 

Each month is stored in another sitemap, one can loop through the months to collect urls from the desired sitemaps.

It can be run as often as one desires once start and end date is updated below
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


# db connection: THIS LINE WILL CHANGE ONCE WE HAVE A NEW DB WORKING AT PENN
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p




headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

source = 'index.hu'

#years = [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022] #update
#months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

years = [2025] #update
months = [1, 2, 3]



baseurl = 'https://index.hu/sitemap/cikkek_'
links = []
for year in years:
    for month in months:
        year_month = str(year) + str(month).zfill(2)
        sitemapurl = baseurl + year_month + '.xml'
        print(sitemapurl)
        reqs = requests.get(sitemapurl, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')
        for link in soup.find_all('loc'):
            links.append(link.text)

links = list(set(links))
print('TOTAL LINKS:', len(links))

clean_links = []
for link in links:
    if '/sport/' in link or '/kultur/' in link or '/techtud/' in link or '/tech/' in link:
        continue
    clean_links.append(link)

  
links = list(set(clean_links))
print('TOTAL LINKS CLEANED:', len(links))



## INSERTING IN THE DB:
url_count = 0
for url in links:
    time.sleep(2)
    if url == "":
        continue
    else:
        if url == None:
            continue
    
    try:
        article = NewsPlease.from_url(url).__dict__
    except:
        time.sleep(1.5)
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

        print("Inserted! in ", colname, " - number of urls so far: ", url_count, 'URL:', url)
    except DuplicateKeyError:
        print("DUPLICATE! Not inserted.")




print("Done inserting ", url_count, "collected urls from ",  source, " into the db.")