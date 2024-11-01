#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 2023

@author: diegoromero

This script updates elkhabar.com using sitemaps.

"""

# Packages:
import time
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
uri = 'mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true'
db = MongoClient(uri).ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## NEED TO DEFINE SOURCE!
source = 'elkhabar.com'

# Custom Parser
def elkhabarcom_story(soup):
    """
    Function to pull the information we want from elkhabar.com stories
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
        listoftexts = soup.findAll("p")
        text = listoftexts[0].text + listoftexts[1].text
        text = text.strip()
        hold_dict['maintext'] = text
    except:
        hold_dict['maintext'] = None  

    # Get Date
    try:
        containsdate = soup.find("time", {"class":"relative_time"})
        containsdate = containsdate['datetime']

        containsdate = containsdate.replace("T"," ")
        containsdate = containsdate.replace("-"," ")
        vectordate = containsdate.split()
        # day, month, year:
        daystr = vectordate[2]
        monthstr = vectordate[1]
        yearstr = vectordate[0]

        article_date = datetime(int(yearstr),int(monthstr),int(daystr))
        hold_dict['date_publish'] = article_date
    except Exception as err:
        hold_dict['date_publish'] = None

    return hold_dict
##

##
sitemap1n = 2022
#https://www.elkhabar.com/sitemap.xml
for i in range(2022,int(sitemap1n)+1):
    ## STEP 1: COLLECTING URLS
    urls = []
    url = "https://elkhabar.com/sitemap-listarticle.xml?yyyy=" + str(i)

    print("Extracting from ", url)
    time.sleep(3)

    reqs = requests.get(url, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    for link in soup.find_all('loc'):
        urlx = link.text
        urls.append(urlx) 

    print("+ Number of urls so far: ", len(urls))

    # STEP 2: Get rid or urls from blacklisted sources + DUPLICATES
    list_urls = list(set(urls))

    print("Total number of USABLE urls found: ", len(list_urls))
    time.sleep(2)

    ## INSERTING IN THE DB:
    url_count = 0
    for url in list_urls:
        if url == "":
            pass
        else:
            if url == None:
                pass
            else:
                if "elkhabar.com" in url:
                    ## SCRAPING USING NEWSPLEASE:
                    try:
                        # count:
                        url_count = url_count + 1
                        #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
                        header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                        response = requests.get(url, headers=header)
                        soup = BeautifulSoup(response.content, 'html.parser')
                        article = NewsPlease.from_html(response.text, url=url).__dict__

                        # add on some extras
                        article['date_download']=datetime.now()
                        article['download_via'] = "Direct2"
                        article['source_domain'] = source
                        article['language'] = 'ar'
                        
                        ## Fixing main texts when needed:                        
                        # Title:
                        article['title'] = elkhabarcom_story(soup)['title']

                        # Main Text
                        article['maintext'] = elkhabarcom_story(soup)['maintext']

                        # Date of Publication
                        article['date_publish'] = elkhabarcom_story(soup)['date_publish']

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
                            print("+ URL: ",url)
                            print("+ DATE: ",article['date_publish'], " - Month: ",article['date_publish'].month)
                            print("+ TITLE: ",article['title'][0:200])
                            print("+ MAIN TEXT: ",article['maintext'][0:200])
                            print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                            pogressm = url_count/len(list_urls)
                            print(" --> Progress:", str(pogressm))
                        except DuplicateKeyError:
                            pogressm = url_count/len(list_urls)
                            print("DUPLICATE! Not inserted. --> Progress:", str(pogressm))
                    except Exception as err: 
                        print("ERRORRRR......", err)
                        #pass
                else:
                    pass

    print("Done inserting ", url_count, " manually collected urls from ",  source)
    time.sleep(2)