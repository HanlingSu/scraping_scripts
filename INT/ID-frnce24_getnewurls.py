#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Nov 11 2021

@author: diegoromero

This script updates france24.com using daily sitemaps.
It can be run as often as one desires. 
"""
# Packages:
import random
import sys
sys.path.append('../')
import os
import re
from p_tqdm import p_umap
from tqdm import tqdm
from pymongo import MongoClient
from urllib.parse import urlparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError, CursorNotFound
import requests
from newsplease import NewsPlease
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import dateparser
import pandas as pd
import time

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# NEED TO DEFINE SOURCE!
source = 'france24.com'

# STEP 0: Define dates
languages = ["es", "fr", "en"]

yearn = "2024"
monthn = 8
daystart = 1
dayend = 31 

months_en = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
months_fr = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
months_es = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

repeat_urls = []
for language in languages:
    if language == "en":
        month_name = months_en[monthn - 1]
    elif language == "fr":
        month_name = months_fr[monthn - 1]
    elif language == "es":
        month_name = months_es[monthn - 1]

    for i in range(int(daystart), int(dayend) + 1):
        # COLLECTING URLS (per day)
        urls = []
        monthstr = f"{monthn:02}"
        daynum = f"{i:02}"

        if language == "en":
            url = f"https://www.france24.com/{language}/archives/{yearn}/{monthstr}/{daynum}-{month_name}-{yearn}"
        elif language == "fr":
            url = f"https://www.france24.com/{language}/archives/{yearn}/{monthstr}/{daynum}-{month_name}-{yearn}"
        elif language == "es":
            url = f"https://www.france24.com/{language}/archivos/{yearn}/{monthstr}/{daynum}-{month_name}-{yearn}"

        print("Extracting from: ", url)
        time.sleep(12)
        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')
        smapurls = []
        for link in soup.find_all('a'):
            urls.append(link.get('href')) 
            smapurls.append(link.get('href')) 
        print("URLs so far: ", len(urls))
        if len(smapurls) == 0:
            repeat_urls.append(url)

        for url in repeat_urls:
            print("Extracting from: ", url)
            time.sleep(12)
            reqs = requests.get(url, headers=headers)
            soup = BeautifulSoup(reqs.text, 'html.parser')
            for link in soup.find_all('a'):
                urls.append(link.get('href')) 
            print("URLs so far: ", len(urls))

        # STEP 1: Get rid of urls from blacklisted sources
        blpatterns = [
            '/sports/', '/sport/', '/tv-shows/', '/culture/', '/archives/', '/voyage/', 
            '/cultura/', '/deportes/', '/video/', '/vidéo/', '/رياضة/', '/ثقافة/', 
            '/ملفاتنا/', '/احذر-الأخبار-الكاذبة', '/fight-the-fake', '/travel/', 
            '/fashion/', '/découvertes/', '/webdocumentaires/', '/stop-infox', '/voyage/', 
            '/programación', '/sports/'
        ]

        clean_urls = []
        for url in urls:
            if url and url != "":
                count_patterns = sum(1 for pattern in blpatterns if pattern in url)
                if count_patterns == 0:
                    clean_urls.append("https://www.france24.com" + url)

        list_urls = list(set(clean_urls))

        print("Total number of USABLE urls found for ", yearn, "/", monthstr, "/", daynum, " is: ", len(list_urls))

        # INSERTING IN THE DB:
        url_count = 0
        for url in list_urls:
            if url and "france24.com" in url:
                print(url, "FINE")
                try:
                    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                    response = requests.get(url, headers=header)
                    article = NewsPlease.from_html(response.text, url=url).__dict__
                    article['date_download'] = datetime.now()
                    article['download_via'] = "Direct2"

                    soup = BeautifulSoup(response.content, 'html.parser')

                    if article['title'] is None:
                        try:
                            contains_title = soup.find("meta", {"property":"og:title"})
                            article['title'] = contains_title["content"]
                        except:
                            try:
                                article['title'] = soup.find('title').text
                            except:
                                article['title'] = None

                    if article['maintext'] is None:
                        try:
                            contains_text = soup.find("meta", {"name":"description"})
                            article['maintext'] = contains_text["content"]
                        except:
                            article['maintext'] = None

                    article['date_publish'] = datetime(int(yearn), int(monthn), int(i))

                    try:
                        year = article['date_publish'].year
                        month = article['date_publish'].month
                        colname = f'articles-{year}-{month}'
                    except:
                        colname = 'articles-nodate'

                    try:
                        db[colname].insert_one(article)
                        url_count += 1
                        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        print("DUPLICATE! Not inserted.")
                except Exception as err:
                    print("ERRORRRR......", err)
                    pass
            else:
                pass

        print("Done inserting ", url_count, " manually collected urls from ", source, " into the db.")
