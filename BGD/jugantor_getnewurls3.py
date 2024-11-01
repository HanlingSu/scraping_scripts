#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Dec 23 2021

@author: diegoromero

This script updates jugantor.com using daily archives.
It can be run whenever necessary.
 
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
import random
from urllib.parse import urlparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from pymongo.errors import CursorNotFound
import requests
from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from dotenv import load_dotenv
from bs4 import BeautifulSoup
# %pip install dateparser
import dateparser
import pandas as pd

# db connection:
db = MongoClient('mongodb://ml4pAdmin:ml4peace@research-devlab-mongodb-01.oit.duke.edu').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## NEED TO DEFINE SOURCE!
source = 'jugantor.com'


## STEP 0: Define dates
## years:
start_year = 2017
end_year = 2019

years = list(range(start_year, end_year+1))

## months:
start_month = 1
end_month = 12
months = list(range(start_month, end_month+1))

months31 = [1,3,5,7,8,10,12]
months30 = [4,6,9,11]

for year in years:
    yearstr = str(year)
    for month in months:
        # Month
        if month <10:
            monthstr = "0" + str(month)
        else:
            monthstr = str(month)
        # defining number of days:
        if month in months31:
            days = list(range(1, 32))
        else:
            if month in months30:
                days = list(range(1, 31))
            else:
                days = list(range(1, 29))
        for day in days:
            ## COLLECTING URLS
            urls = []

            # Day
            if day <10:
                daystr = "0" + str(day)
            else:
                daystr = str(day)
            # OBTAINING URLS FROM THE DAY (bn)
            if year <=2015:
                #https://www.jugantor.com/old/2013/09/29
                url = "https://www.jugantor.com/old/" + yearstr + "/" + monthstr + "/" + daystr
            else:
                if year <=2017:
                    #https://www.jugantor.com/news-archive/today-print-edition/2016/09/29
                    #https://www.jugantor.com/news-archive/online/2016/09/29
                    url = "https://www.jugantor.com/news-archive/" + yearstr + "/" + monthstr + "/" + daystr
                else:
                    #https://www.jugantor.com/archive/2018/01/01
                    url = "https://www.jugantor.com/archive/" + yearstr + "/" + monthstr + "/" + daystr

            print("Extracting from ", url)

            reqs = requests.get(url, headers=headers)
            soup = BeautifulSoup(reqs.text, 'html.parser')

            for link in soup.find_all('a'):
                urls.append(link.get('href')) 
                #print(link.get('href'))

            ### PREPARING THE DAY'S URLS:
            # List of unique urls:
            dedup = list(set(urls))
            # Get rid or urls from blacklisted sources
            blpatterns = ['/editorial','/islam-and-life','/images','/news_images','/news_photos','/cache-images','/everyday','/feed/','/lifestyle','/literature','/opinion','/social-media','/sports','/jugantor-22-anniv/','/video-gallery','/viewers-opinion']
            list_urls = []
            for url in dedup:
                if url == "":
                    pass
                else:
                    if url == None:
                        pass
                    else:
                        if url == "#":
                            pass
                        else:
                            if "jugantor.com" in url:
                                count_patterns = 0
                                for pattern in blpatterns:
                                    if pattern in url:
                                        count_patterns = count_patterns + 1
                                if count_patterns == 0:
                                    list_urls.append(url)
            printbit = "Total number of USABLE urls found for " + yearstr + "-" + monthstr + "-" + daystr + ": "
            print(printbit, len(list_urls))
            
            ## INSERTING IN THE DB:
            url_count = 0
            for url in list_urls:
                if url == "":
                    pass
                else:
                    if url == None:
                        pass
                    else:
                        if "jugantor.com" in url:
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
                                
                                ## Need to fix things before adding to the db
                                soup = BeautifulSoup(response.content, 'html.parser')

                                ## Correct Title:
                                if "/old/" in url:
                                    try: 
                                        article_title = soup.find("h3", {"class":"font-weight-bolder"}).text
                                        article['title']  = article_title 
                                    except:
                                        article_title = article['title']
                                        article['title'] = article_title
                                else:
                                    try:
                                        contains_title = soup.find("meta", {"property":"og:title"})
                                        article_title = contains_title['content']
                                        if "Breaking News" in article_title:
                                            article_title = soup.find("h3", {"class":"font-weight-bolder"}).text
                                            article['title']  = article_title 
                                        else:
                                            article['title']  = article_title   
                                    except:
                                        article_title = article['title']
                                        article['title'] = article_title                                   

                                ## Correct Main Text:
                                try:
                                    maintext_contains = soup.findAll("p")
                                    maintext = maintext_contains[0].text + " " + maintext_contains[1].text + " " + maintext_contains[2].text
                                    article['maintext'] = maintext
                                except: 
                                    maintext = article['maintext']
                                    article['maintext'] = maintext

                                ## FIX date:
                                #if article['date_publish']
                                if article['date_publish'] == None:
                                    article_date = datetime(int(year),int(month),int(day))
                                    article['date_publish'] = article_date

                                    
                                # Choosing the correct db collection:
                                try:
                                    yearx = article['date_publish'].year
                                    monthx = article['date_publish'].month
                                    if yearx != year:
                                        if monthx != month:
                                            colname = f'articles-{year}-{month}'
                                        else:
                                            colname = f'articles-{year}-{month}'
                                    else:
                                        colname = f'articles-{yearx}-{monthx}'
                                    #print(article)
                                except:
                                    colname = 'articles-nodate'
                                try:
                                    #TEMP: deleting the stuff i included with the wrong domain:
                                    #myquery = { "url": final_url, "source_domain" : 'web.archive.org'}
                                    #db[colname].delete_one(myquery)
                                    # Inserting article into the db:
                                    db[colname].insert_one(article)
                                    # count:
                                    url_count = url_count + 1
                                    #print(url)
                                    #print(article['date_publish'])
                                    #print(article['title'][0:20])
                                    #print("TEXT: ",article['maintext'][0:60])
                                    print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                                    db['urls'].insert_one({'url': article['url']})
                                except DuplicateKeyError:
                                    print("DUPLICATE! Not inserted.")
                            except Exception as err: 
                                print("ERRORRRR......", err)
                                pass
                        else:
                            pass

            print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db. DATE:" , yearstr, "-", monthstr, "-", daystr)