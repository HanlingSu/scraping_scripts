#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Nov 11 2021

@author: diegoromero

This script updates telegraphindia.com 
 
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

import math

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


## NEED TO DEFINE SOURCE!
source = 'telegraphindia.com'

monthupdate = 3
yearupdate = 2023

def telegraphindiacom_story(soup):
    """
    Function to pull the information we want from telegraphindia.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}

    # Get Title: 
    try:
        article_title = soup.find("title").text
        hold_dict['title']  = article_title   
    except:
        try:
            article_titlec = soup.find("meta", {"property":"og:title"})
            article_title = article_titlec["content"] 
            hold_dict['title']  = article_title 
        except:
            hold_dict['title']  = None
        
    # Get Main Text:
    try:
        sentences = soup.findAll("p")
        #print(len(sentences))
        text = ""
        count = 0
        for sent in sentences:
            count = count + 1
            if count >= 6:
                text = text + " " + sent.text
            else:
                pass
        #text = text.replace("</p>, <p><em>", "")
        #text = text.replace("</p>, <p>", "")
        #text = text.replace("[<p>", "")
        text = text.lstrip()
        hold_dict['maintext'] = text
    except:
        hold_dict['maintext'] = None  

    # Get Date
    try:
        containsdate = soup.find("div",{"class":"fs-12 float-left"}).text
        datevector = containsdate.split("Published ")
        datevector = datevector[1].split(", ")
        datebit = datevector[0].replace(".", " ")
        datevector = datebit.split()
        dayx = datevector[0]
        monthx = datevector[1]
        yearx = datevector[2]
        year = int(yearx) + 2000

        article_date = datetime(year,int(monthx),int(dayx))
        hold_dict['date_publish'] = article_date
    except:
        try:
            containsdate = soup.find("div",{"class":"enpublicdate mt24 dfjsb aic"}).text
            datevector = containsdate.split("Published ")
            datevector = datevector[1].split(", ")
            datebit = datevector[0].replace(".", " ")
            datevector = datebit.split()
            dayx = datevector[0]
            monthx = datevector[1]
            yearx = datevector[2]
            year = int(yearx) + 2000

            article_date = datetime(year,int(monthx),int(dayx))
            hold_dict['date_publish'] = article_date
        except:
            hold_dict['date_publish'] = None
   
    return hold_dict 

# empty searchers: -> 999 pages, only goes back to Dec 2022. 
for j in range(1,1000):
    # Step 1: obtain urls in each page
    urls = []
    urlsections = ["https://www.telegraphindia.com/search?keyword=&page=", "https://www.telegraphindia.com/west-bengal/page-", "https://www.telegraphindia.com/north-east/page-","https://www.telegraphindia.com/jharkhand/page-","https://www.telegraphindia.com/india/page-","https://www.telegraphindia.com/opinion/page-","https://www.telegraphindia.com/world/page-","https://www.telegraphindia.com/business/page-"]
    
    for baseurl in urlsections:
        url = baseurl + str(j)
        print(url)
        req = requests.get(url, headers = headers)
        soup = BeautifulSoup(req.content, 'html.parser')

        for link in soup.find_all('a'):
            urls.append(link.get('href')) 

    # Step 2: Get rid or urls from blacklisted sources and fix urls
    blpatterns = ['/sports/','/entertainment/','/gallery/']
    clean_urls = []
    for url in urls:
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
                    if not "https://www.telegraphindia.com/" in url:
                        url = "https://www.telegraphindia.com" + url
                    clean_urls.append(url)
        
    list_urls = list(set(clean_urls))
    print("Total number of USABLE urls found: ", len(list_urls))



    ## INSERTING IN THE DB:
    url_count = 0
    for url in list_urls:
        print(url)
        ## SCRAPING USING NEWSPLEASE:
        try:
            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            response = requests.get(url, headers=header)
            # process
            article = NewsPlease.from_html(response.text, url=url).__dict__
            # add on some extras
            article['date_download'] = datetime.now()
            article['download_via'] = "LocalIND"
            article['source_domain'] = source 
            
            #if '/en/' in url:
            #    article['language'] = 'en'
            #article['language'] = 'es'
            
            ## Fixing Date + Title + Main Text
            soup = BeautifulSoup(response.content, 'html.parser')

            article['date_publish'] = telegraphindiacom_story(soup)['date_publish']
            article['title'] = telegraphindiacom_story(soup)['title']
            article['maintext'] = telegraphindiacom_story(soup)['maintext']

            #try:
            #    contains_date = soup.find("div", {"class":"post-meta-date"}).text
                #contains_date = soup.find("i", {"class":"fa fa-calendar"}).text
            #    article_date = dateparser.parse(contains_date, date_formats=['%d/%m/%Y'])
            #    article['date_publish'] = article_date
            #except:
            #    article_date = article['date_publish']
            #    article['date_publish'] = article_date
              # Define collection to update:
            colname_toupdate = f'articles-{yearupdate}-{monthupdate}'
            ## Inserting into the db
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'articles-{year}-{month}'
            except:
                colname = 'articles-nodate'
            try:
                if colname == colname_toupdate: 
                    url_count = url_count + 1
                    # Inserting article into the db:
                    db[colname].insert_one(article)
                    print(" + Date: ", article['date_publish'], " + Main Text: ", article['maintext'][0:50], " + Title: ", article['title'][0:25])
                    print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                else: 
                    print("Not in desired collection.")
            except DuplicateKeyError:
                print("DUPLICATE! Not inserted.")
        except Exception as err: 
            print("ERRORRRR......", err)
            pass

    print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")














# section by section: only shows 999 pages
#https://www.telegraphindia.com/india
#https://www.telegraphindia.com/india/page-999













