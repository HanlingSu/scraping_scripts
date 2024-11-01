"""
Created on July 22 2022

@author: serkantadiguzel

This script fixes 'firstpost.com' problematic URLs.

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


d = pd.read_csv('urls_need_recollection.csv')

links_list = list(set(list(d['0'])))


## INSERTING IN THE DB:
url_count = 0
for url in links_list:

    if url == "":
        continue
    else:
        if url == None:
            continue
    
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

            continue


    print('Date extracted:', correct_date_final)

    # add on some extras
    article['date_download']=datetime.now()
    article['download_via'] = "Direct2" #change
    article['source_domain'] = source

    # add a fix: highlighted section is in the description so we can add that part to the maintext too
    try:
        article['maintext'] = article['description'] + ' ' + article['maintext']
    except:
        pass


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

