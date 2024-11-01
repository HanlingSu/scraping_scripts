#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Dec 27 2021

@author: diegoromero

This script updates jomhouria.com using section query.
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


def jomhouriacom_story(soup):
    """
    Function to pull the information we want from jomhouria.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}

    # Get Title: 
    try:
        contains_title = soup.find("meta", {"property":"og:title"})
        article_title = contains_title['content']
        hold_dict['title']  = article_title   
    except:
        article_title = None
        hold_dict['title']  = None
        
    # Get Main Text:
    try:
        contains_text = soup.findAll('p',{"style":"text-align: justify;"})
        if len(contains_text) > 1:
          if len(contains_text) == 2:
            maintext = contains_text[0].text + contains_text[1].text
          else:
            maintext = contains_text[0].text + contains_text[1].text + contains_text[2].text
        else:
          maintext = contains_text[0].text
        hold_dict['maintext'] = maintext
    except: 
        try:
            contains_maintext = soup.find("meta", {"property":"og:description"})
            maintext = contains_maintext['content']
            hold_dict['maintext'] = maintext  
        except: 
            maintext = None
            hold_dict['maintext']  = None

    # Get Date
    try:
        contains_date = soup.find("div", {"style":"float:right; margin-right:8px; padding-right:36px; width:200px; font-size:12px; font-weight:normal; background:url(images/cal.png) no-repeat top right"}).text
        monthstr = contains_date.split()[3]
        monthstr = monthstr.strip()
        dayx =contains_date.split()[2]
        dayx = dayx.strip()
        yearx = contains_date.split()[4]
        yearx = yearx.strip()
        # List of months:
        dec = "ديسمبر"
        nov = "نوفمبر"
        oct = "أكتوبر"
        sep = "سبتمبر"
        aug = "أوت"
        jul = "جويلية"
        jun = "جوان"
        may = "ماي"
        apr = "أفريل"
        mar = "مارس"
        feb = "فيفري"
        jan = "جانفي"

        if monthstr == dec:
          monthn = 12
        else:
          if monthstr == nov:
            monthn = 11
          else:
            if monthstr == oct:
              monthn = 10
            else:
              if monthstr == sep:
                monthn = 9
              else:
                if monthstr == aug:
                  monthn = 8
                else:
                  if monthstr == jul:
                    monthn = 7
                  else:
                    if monthstr == jun:
                      monthn = 6
                    else:
                      if monthstr == may:
                        monthn = 5
                      else:
                        if monthstr == apr:
                          monthn = 4
                        else:
                          if monthstr == mar:
                            monthn = 3
                          else:
                            if monthstr == feb:
                              monthn = 2
                            else:
                              if monthstr == jan:
                                monthn = 1

        article_date = datetime(int(yearx),int(monthn),int(dayx))
        hold_dict['date_publish'] = article_date 
    except:
        hold_dict['date_publish'] = None
   
    return hold_dict 


# db connection:
db = MongoClient('mongodb://ml4pAdmin:ml4peace@research-devlab-mongodb-01.oit.duke.edu').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## NEED TO DEFINE SOURCE!
source = 'jomhouria.com'

## STEP 0: OBTAINING URLS:
urls = []
# complete scraping:
#for i in range(1,13173): 
# updating:
for i in range(1,300): 
    #https://www.jomhouria.com/index.php?art=1&page=13172
    url = "https://www.jomhouria.com/index.php?art=1&page=" + str(i)
    print("Extracting from ", url)

    reqs = requests.get(url, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    soup = BeautifulSoup(reqs.content, 'html.parser')
    for link in soup.find_all('a'):
        urls.append(link.get('href')) 

### PREPARING THE DAY'S URLS:
# List of unique urls:
list_urls = []
dedup = list(set(urls))

for url in dedup:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if "page=" in url:
                pass
            else:
                if "art" in url:
                    newurl = "https://www.jomhouria.com/" + url
                    list_urls.append(newurl)
                else:
                    pass

print("Number of usable urls: ", len(list_urls))

#df = pd.DataFrame(list_urls)
#df.to_csv('/Users/diegoromero/Downloads/jomhouria_check.csv')

## INSERTING IN THE DB:
url_count = 0
for url in list_urls:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if "jomhouria.com" in url:
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
                    
                    # FIXING: DATE, TITLE, MAIN TEXT
                    hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                    req = requests.get(url, headers = hdr)
                    soup = BeautifulSoup(req.text, 'html.parser')

                    article['title'] = jomhouriacom_story(soup)['title']
                    article['maintext'] = jomhouriacom_story(soup)['maintext']
                    article['date_publish'] = jomhouriacom_story(soup)['date_publish']

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
                        print("+ DATE:: ", article['date_publish'])
                        print("+ TITLE: ", article['title'][0:200])
                        print("+ MAIN TEXT: ", article['maintext'][0:200])
                        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        print("DUPLICATE! Not inserted.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
            else:
                pass

print("Done inserting ",url_count, " manually collected urls from ",source, " into the db.")