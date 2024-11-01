#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Dec 23 2021

@author: diegoromero

This script updates prothomalo.com using daily sitemaps.
It can be run whenever necessary.
 
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


def prothomalocom_story(soup):
    """
    Function to pull the information we want from prothomalo.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}

    # Get Title: 
    try:
        #article_title = soup.find("title").text
        contains_title = soup.find("meta", {"property":"og:title"})
        article_title = contains_title['content']
        hold_dict['title']  = article_title   
    except:
        try:
            article_title = soup.find("title").text
            hold_dict['title']  = article_title   
        except:
            article_title = None
            hold_dict['title']  = None
        
    # Get Main Text:
    try:
        maintext_contains = soup.findAll("p")
        maintext = maintext_contains[0].text + " " + maintext_contains[1].text + " " + maintext_contains[2].text
        hold_dict['maintext'] = maintext
    except: 
        try:
            maintext_contains = soup.findAll("p")
            maintext = str(maintext_contains[0])
            maintext = maintext.replace("<p>","")
            maintext = maintext.replace("</p>","")
            hold_dict['maintext'] = maintext
        except: 
            maintext = None
            hold_dict['maintext']  = None

    # Get Date
    try: 
        containsdate = soup.find("div", {"class":"storyPageMetaData-m__publish-time__19bdV"})
        containsdate = str(containsdate)
        indexdatetime = containsdate.index("datetime")
        usablebit = containsdate[indexdatetime+10:]
        indexx = usablebit.index('">')
        datex = usablebit[:indexx]
        article_date = dateparser.parse(datex)
        hold_dict['date_publish'] = article_date  
    except:
        try:
            contains_date = soup.find("time", {"class":"published-time"}).text
            article_date = dateparser.parse(contains_date)  
            hold_dict['date_publish'] = article_date  
        except:
            hold_dict['date_publish'] = None
   
    return hold_dict 


# db connection:
db = MongoClient('mongodb://ml4pAdmin:ml4peace@research-devlab-mongodb-01.oit.duke.edu').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## NEED TO DEFINE SOURCE!
source = 'prothomalo.com'

## STEP 0: Define dates
## years:
start_year = 2017
end_year = 2017

years = list(range(start_year, end_year+1))

## months:
start_month = 9
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
            url = "https://prothomalo.com/sitemap/sitemap-daily-" + yearstr + "-" + monthstr + "-" + daystr + ".xml"
            
            print("Extracting from ", url)

            reqs = requests.get(url, headers=headers)
            #soup = BeautifulSoup(reqs.text, 'html.parser')
            soup = BeautifulSoup(reqs.content, 'html.parser')
            for link in soup.findAll('loc'):
                urls.append(link.text)

            url = "https://en.prothomalo.com/sitemap/sitemap-daily-" + yearstr + "-" + monthstr + "-" + daystr + ".xml"
            print("Extracting from ", url)

            reqs = requests.get(url, headers=headers)
            #soup = BeautifulSoup(reqs.text, 'html.parser')
            soup = BeautifulSoup(reqs.content, 'html.parser')
            for link in soup.findAll('loc'):
                urls.append(link.text)

            ### PREPARING THE DAY'S URLS:
            # List of unique urls:
            dedup = list(set(urls))
            # Get rid or urls from blacklisted sources
            blpatterns = ['/poll/','/art-and-literature/','/opinion','/life-style/','/lifestyle','/education/','/special-supplement/','/entertainment','/feature','/photo','/sports','/video','/personal-finance/','/chakri-suggestion/','/fun/','/life/']
            list_urls = []
            for url in dedup:
                if url == "":
                    pass
                else:
                    if url == None:
                        pass
                    else:
                        if "prothomalo.com" in url:
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
                        if "prothomalo.com" in url:
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
                                

                                if "en.prothomalo" in url:
                                    #print("OLD: ", article['date_publish'])
                                    ## Inserting into the db (ONLY need to fix date)
                                    hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                                    req = requests.get(url, headers = hdr)
                                    soup = BeautifulSoup(req.text, 'html.parser')

                                    ## FIX date:
                                    try: 
                                        containsdate = soup.find("div", {"class":"storyPageMetaData-m__publish-time__19bdV storyPageMetaData-m__no-update__3AA06"})
                                        containsdate = str(containsdate)
                                        indexdatetime = containsdate.index("datetime")
                                        usablebit = containsdate[indexdatetime+10:]
                                        indexx = usablebit.index('">')
                                        datex = usablebit[:indexx]
                                        article_date = dateparser.parse(datex)
                                        article['date_publish'] = article_date  
                                    except:
                                        article_date = datetime(int(year),int(month),int(day))
                                        article['date_publish'] = article_date 
                                    #print("NEW: ", article['date_publish'])
                                    # Choosing the correct db collection:
                                    try:
                                        year = article['date_publish'].year
                                        month = article['date_publish'].month
                                        colname = f'articles-{year}-{month}'
                                        #print(article)
                                    except:
                                        colname = 'articles-nodate'
                                else:
                                    ## Need to fix things before adding to the db
                                    hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                                    req = requests.get(url, headers = hdr)
                                    soup = BeautifulSoup(req.text, 'html.parser')

                                    ## FIX title:
                                    try:
                                        #article_title = soup.find("title").text
                                        contains_title = soup.find("meta", {"property":"og:title"})
                                        article_title = contains_title['content']
                                        article['title']  = article_title   
                                    except:
                                        try:
                                            article_title = soup.find("title").text
                                            article['title']  = article_title   
                                        except:
                                            article_title = article['title']
                                            article['title'] = article_title

                                    ## FIX main text:
                                    try:
                                        maintext_contains = soup.findAll("p")
                                        maintext = maintext_contains[0].text + " " + maintext_contains[1].text + " " + maintext_contains[2].text
                                        article['maintext'] = maintext
                                    except: 
                                        try:
                                            maintext_contains = soup.findAll("p")
                                            maintext = str(maintext_contains[0])
                                            maintext = maintext.replace("<p>","")
                                            maintext = maintext.replace("</p>","")
                                            article['maintext'] = maintext
                                        except: 
                                            maintext = article['maintext']
                                            article['maintext'] = maintext

                                    ## FIX date:
                                    try: 
                                        containsdate = soup.find("div", {"class":"storyPageMetaData-m__publish-time__19bdV"})
                                        containsdate = str(containsdate)
                                        indexdatetime = containsdate.index("datetime")
                                        usablebit = containsdate[indexdatetime+10:]
                                        indexx = usablebit.index('">')
                                        datex = usablebit[:indexx]
                                        article_date = dateparser.parse(datex)
                                        article['date_publish'] = article_date  
                                    except:
                                        try:
                                            contains_date = soup.find("time", {"class":"published-time"}).text
                                            article_date = dateparser.parse(contains_date)  
                                            article['date_publish'] = article_date  
                                        except:
                                            article_date = datetime(int(year),int(month),int(day))
                                            article['date_publish'] = article_date 
                                            #article_date = article['date_publish']
                                            #article['date_publish'] = article_date 
                                    
                                    # Choosing the correct db collection:
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
                                    url_count = url_count + 1
                                    print("URL: ",url)
                                    #print("+ DATE:: ", article['date_publish'])
                                    print("+ TITLE: ", article['title'][0:20])
                                    print("+ MAIN TEXT: ", article['maintext'][0:50])
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