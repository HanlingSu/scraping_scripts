#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Dec 27 2021

@author: diegoromero

This script updates dailyjanakantha.com using daily archives.
It at least once every two months
 
"""
# Packages:
import random
import importlib
import sys
sys.path.append('../')
import os
import re
#from p_tqdm import p_umap
from tqdm import tqdm
from pymongo import MongoClient
import random
from urllib.parse import urlparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from pymongo.errors import CursorNotFound
import requests
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
source = 'dailyjanakantha.com'

## STEP 0: Define dates
## years:
start_year = 2022
end_year = 2022

years = list(range(start_year, end_year+1))

## months:
start_month = 6
end_month = 6
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
            sections = ['frontpage','lastpage','others','national','international']

            for sect in sections:
                url = "https://www.dailyjanakantha.com/print-media/" + yearstr + "-" + monthstr + "-" + daystr + "/" + sect + "/"
                print("Extracting from ", url)
                #https://www.dailyjanakantha.com/print-media/2021-12-06/frontpage/
                #https://www.dailyjanakantha.com/print-media/2014-11-06/lastpage/
                #https://www.dailyjanakantha.com/print-media/2014-11-06/others/
                #https://www.dailyjanakantha.com/print-media/2014-11-06/national/
                #https://www.dailyjanakantha.com/print-media/2014-11-06/international/

                reqs = requests.get(url, headers=headers)
                soup = BeautifulSoup(reqs.text, 'html.parser')

                for link in soup.find_all('a'):
                    urls.append(link.get('href')) 

            ### PREPARING THE DAY'S URLS:
            # List of unique urls:
            dedup = list(set(urls))
            # Get rid or urls from blacklisted sources

            blpatterns = ['edaily','/itdotcom/','/eid-binodon/','/digitalgeneration/','/fashion/','/editorial/','/education/','/glittering/','/literature/','/reopinion/','/feature-page/','/print-media/','/periodicals/']
            list_urls = []

            for url in dedup:
                
                if "#" in url:
                    pass
                else:
                    if url == "":
                        pass
                    else:
                        if url == None:
                            pass
                        else: 
                            if "dailyjanakantha.com" in url:
                                count_patterns = 0
                                for pattern in blpatterns:
                                    if pattern in url:
                                        count_patterns = count_patterns + 1
                                if count_patterns == 0:
                                    list_urls.append(url)
                            else: 
                                count_patterns = 0
                                for pattern in blpatterns:
                                    if pattern in url:
                                        count_patterns = count_patterns + 1
                                if count_patterns == 0:
                                    urlnew = "https://www.dailyjanakantha.com" + url
                                    list_urls.append(urlnew)

            blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
            blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
            list_urls = [word for word in list_urls if not blacklist.search(word)]

            printbit = "Total number of USABLE urls found for " + yearstr + "-" + monthstr + "-" + daystr + ": "
            print(printbit, len(list_urls))

            ## INSERTING IN THE DB:
            url_count = 0
            processed_url_count = 0
            for url in list_urls:
                print(url)
                if url == "":
                    pass
                else:
                    if url == None:
                        pass
                    else:
                        if "dailyjanakantha.com" in url:
                            #print(url, "FINE")
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
                                article['language'] = "bn"
                                
                                ## Fixing Date:
                                soup = BeautifulSoup(response.text, 'html.parser')

                                # Get Title: 
                                try:
                                    contains_title = soup.find("meta", {"property":"og:title"})
                                    article_title = contains_title['content']
                                    article['title']  = article_title   
                                except:
                                    article_title = article['title']
                                    article['title'] = article_title
                                print('Title scraped', article['title'] )
                                # Get Main Text:
                                try:
                                    soup.find("div", {'id' : 'contentDetails'}).find_all('p')
                                    for i in soup.find("div", {'id' : 'contentDetails'}).find_all('p'):
                                        maintext += i.text
                                    article['maintext'] = maintext.strip()
                                except:
                                    try:
                                        maintext_contains = soup.findAll("p")
                                        maintext = maintext_contains[0].text + " " + maintext_contains[1].text + " " + maintext_contains[2].text
                                        article['maintext'] = maintext
                                    except: 
                                        maintext = article['maintext']
                                        article['maintext'] = maintext
                                print('Maintext scraped', article['maintext'])
                                # Get Date
                                try:
                                    ## YEARS 
                                    year_bn = ["২০১২", "২০১৩", "২০১৪", "২০১৫", "২০১৬", "২০১৭", "২০১৮", "২০১৯", "২০২০", "২০২১", "২০২২", "২০২৩", "২০২৪", "২০২৫", "২০২৬"]
                                    year_n = ["2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]

                                    ## DAYS (IN NUMBERS)
                                    number_bn = ["০১", "০২", "০৩", "০৪", "০৫", "০৬", "০৭", "০৮", "০৯","১০", "১১", "১২", "১৩", "১৪", "১৫", "১৬", "১৭", "১৮", "১৯", "২০", "২১", "২২", "২৩", "২৪", "২৫", "২৬", "২৭", "২৮", "২৯", "৩০", "৩১"]

                                    ## MONTHS
                                    month_bn = ["জানুয়ারী","ফেব্রুয়ারী","মার্চ","এপ্রিল","মে","জুন","জুলাই","আগস্ট","সেপ্টেম্বর","অক্টোবর","নভেম্বর","ডিসেম্বর"]

                                    contains_date = soup.find("b").text
                                    vectordate = contains_date.split()
                                    monthstrx = vectordate[0]
                                    daystrx = vectordate[1]
                                    daystrx = daystrx.replace(",","")
                                    yearstrx = vectordate[2]
                                    # Numbers:
                                    monthx = month_bn.index(monthstrx) + 1 
                                    dayx = number_bn.index(daystrx) + 1 
                                    yearindex = year_bn.index(yearstrx)
                                    yearx = year_n[yearindex]

                                    article_date = datetime(int(yearx),int(monthx),int(dayx))
                                    article['date_publish'] = article_date 
                                except:
                                    article_date = datetime(int(year),int(month),int(day))
                                    article['date_publish'] = article_date 
                                print('Date scraped', article['date_publish'] )

                                ## Inserting into the db
                                try:
                                    year = article['date_publish'].year
                                    month = article['date_publish'].month
                                    colname = f'articles-{year}-{month}'
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
                                    if colname != 'articles-nodate':
                                        url_count = url_count + 1
                                        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                                    else:
                                        print("Inserted! in ", colname)
                                    db['urls'].insert_one({'url': article['url']})

                                except DuplicateKeyError:
                                    # myquery = { "url": url}
                                    # db[colname].delete_one(myquery)
                                    # # Inserting article into the db:
                                    # db[colname].insert_one(article)
                                    # print("DUPLICATE! UPDATED.")
                                    pass
                                    print("DUPLICATE! Not inserted.")
                            except Exception as err: 
                                print("ERRORRRR......", err)
                                pass
                            processed_url_count += 1
                            print('\n',processed_url_count, '/', len(list_urls), 'articles have been processed ...\n')

                        else:
                            pass

            print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db. DATE:" , yearstr, "-", monthstr, "-", daystr)