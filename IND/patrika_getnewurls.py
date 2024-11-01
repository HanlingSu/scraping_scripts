#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Jun 6 2023

@author: diegoromero

This script updates patrika.com using daily sitemaps
It can be run as often as one desires. 

Sitemaps:
https://www.patrika.com/sitemap.xml
https://www.patrika.com/newsindex.xml
https://www.patrika.com/googlenewssitemap1.xml
https://www.patrika.com/googlenewssitemap2.xml
https://www.patrika.com/urlsitemapindex.xml

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
#from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from dotenv import load_dotenv
from bs4 import BeautifulSoup
# %pip install dateparser
import dateparser
import pandas as pd

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
#db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
#db = MongoClient('mongodb://ml4pAdmin:ml4peace@research-devlab-mongodb-01.oit.duke.edu').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


## NEED TO DEFINE SOURCE!
source = 'patrika.com'
#https://www.patrika.com/google-sitemap.xml?dt=2015-02-07


## STEP 0: Define dates
# Note: URLs lead to pages not found in archives from before 2017
#yearlist = ["2024","2023", "2022"]
yearlist = ["2024"] #(June to Dec)
#yearmonths = ["/2021/10/","/2022/08/"]]

list31 = [1,3,5,7,8,10,12]
list30 = [4,6,9,11]

########################################
##            Custom parser           ##   
########################################
def patrikacom_story(soup):
    """
    Function to pull the information we want from patrika.com stories
    """
    hold_dict = {}

    # Get Title: 
    try:
        article_titlec = soup.find("meta", {"property":"og:title"})
        article_title = article_titlec["content"]
        hold_dict['title']  = article_title   
    except:
        try:
            article_title = soup.find("title").text
            hold_dict['title']  = article_title 
        except:
            hold_dict['title']  = None
        
    # Get Main Text:
    try:
        text = soup.find("div",{"class":"fontTextnew my-4 md:text-lg text-base mx-5 md:mx-0"}).text
        text = text.strip()
        hold_dict['maintext'] = text
    except:
        hold_dict['maintext'] = None  

    # Get Date
    try:
        #meta property="article:modified_time"
        containsdate = soup.find("meta", {"property":"article:published_time"})
        article_date = containsdate['content']
        hold_dict['date_publish'] = dateparser.parse(article_date)
    except Exception as err:
        hold_dict['date_publish'] = None
        #print("Error when trying to get the date", err)

    return hold_dict
########################################

for ym in yearlist:
    for mth in range(1,13):
        print(ym, " and month: ", str(mth))
        ## COLLECTING URLS
        urls = []
        
        if mth <10:
            mthstr = "0" + str(mth)
        else:
            mthstr = str(mth)

        # Defining how many days
        if mth in list31:
            lastday = 32
        else:
            if mth in list30:
                lastday = 31
            else:
                lastday = 29
        
        # Scraping urls from each year-moth-day archive
        for i in range(1, lastday): 
            if i <10:
                daynum = "0" + str(i)
            else:
                daynum = str(i)
            
            url = "https://www.patrika.com/google-sitemap.xml?dt=" + str(ym) + "-" + mthstr + "-" + daynum
            print("Extracting from: ", url)

            reqs = requests.get(url, headers=headers)
            soup = BeautifulSoup(reqs.text, 'html.parser')
            for link in soup.findAll('loc'):
                urls.append(link.text)
            #for link in soup.find_all('a'):
            #    urls.append(link.get('href')) 
            print("URLs so far: ", len(urls))

        # Scraping all the articles for the month

        # STEP 1: Get rid or urls from blacklisted sources
        # List of unique urls:
        dedup_urls = list(set(urls))

        blpatterns = ['/entertainment-news/','/astrology-and-spirituality','/weird-news/','/recipes/','/sports-news/','/exam-tips-tricks/']
        list_urls = []
        for url in dedup_urls:
            if url == "":
                pass
            else:
                if url == None:
                    pass
                else:
                    count_patterns = 0
                    for pattern in blpatterns:
                        if pattern in url:
                            count_patterns = count_patterns + 1
                    if count_patterns == 0:
                        list_urls.append(url)

        print("Total number of USABLE urls found: ", len(list_urls), " from: ", str(ym), "-", mthstr)


        ## INSERTING IN THE DB:
        url_count = 0
        for url in list_urls:
            if url == "":
                pass
            else:
                if url == None:
                    pass
                else:
                    if 'patrika.com' in url:
                        print("+ URL: ", url)
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
                            article['source_domain'] = 'patrika.com'
                            
                            ## Fixing Date, Title, and Text
                            soup = BeautifulSoup(response.content, 'html.parser')

                            # Title:
                            article['title'] = patrikacom_story(soup)['title']

                            # Text:
                            article['maintext'] = patrikacom_story(soup)['maintext']

                            # Date: 
                            article['date_publish'] = patrikacom_story(soup)['date_publish']

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
                                url_count = url_count + 1
                                #print(article['date_publish'])
                                #print(article['date_publish'].month)
                                print("+ TITLE: ", article['title'][0:80])
                                print("+ TEXT: ", article['maintext'][0:100])
                                print("+ DATE: ", article['date_publish'])
                                print("+ Inserted in ", colname, " - number of urls so far: ", url_count)
                            except DuplicateKeyError:
                                print("DUPLICATE! Not inserted.")
                        except Exception as err: 
                            print("ERRORRRR......", err)
                            pass
                    else:
                        pass


        print("Done inserting ", url_count, " manually collected urls from ", str(ym), "-", mthstr)