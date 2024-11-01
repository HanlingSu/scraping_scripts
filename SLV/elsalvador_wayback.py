#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Nov 11 2021

@author: diegoromero

"""
# Packages:
import random
import sys
import os
import re

import requests as rq
import urllib.request
from bs4 import BeautifulSoup
import dateparser
from time import sleep
from time import time
from random import randint
from warnings import warn
import json
import pandas as pd
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
#from dotenv import load_dotenv



## DEFINE PERIOD (FORMAT: YYYYMMDD)
# from date:
fromdate = "20170401" 
# to date:
todate = "20190430"

## DEFINE SOURCE(S):
sources = ['ferloo.com']

# DEFINE DABASE:
uri = 'mongodb://ml4pAdmin:ml4peace@research-devlab-mongodb-01.oit.duke.edu'
db = MongoClient(uri).ml4p

sources = ["elsalvador.com"]

# Custom Parser:
def elsalvadorcom_story(soup):
    """
    Function to pull the information we want from elsalvador.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    
    # Get Title: 
    try:
        contains_title = soup.find("meta", {"property":"og:title"})
        article_title = contains_title['content']
        hold_dict['title']  = article_title   
    except:
        try:
            article_title = soup.find("title").text
            hold_dict['title']  = article_title   
        except:
            hold_dict['title']  = None
        
    # Get Main Text:
    try:
        contains_maintext = soup.find("meta", {"property":"og:description"})
        article_maintext = contains_maintext['content']
        hold_dict['maintext'] = article_maintext
    except: 
        try: 
            maintext_contains = soup.findAll("p")
            maintext = maintext_contains[2].text + " " + maintext_contains[3].text + " " + maintext_contains[4].text
            hold_dict['maintext'] = maintext
        except:
            maintext = None
            hold_dict['maintext']  = None

    # Get Date (not for /amp/)
    try:  
        contains_date = soup.find("meta", {"property":"article:published_time"})
        article_date = contains_date['content']
        #article_date = dateparser.parse(article_date,date_formats=['%d/%m/%Y'])
        article_date = dateparser.parse(article_date)
        hold_dict['date_publish'] = article_date  
    except:
        try:
            contains_date = soup.find("meta", {"name":"moddate"})
            article_date = contains_date['content']
            article_date = dateparser.parse(article_date)
            hold_dict['date_publish'] = article_date 
            #name="moddate" content="2017-01-02T18:47:45-06:00"
        except:
            try:
                datex = soup.find("span", {"class":"ago"}).text
                datex = datex.replace(",", "")
                datex = datex.replace("-", "")
                datex = datex.replace(".", "")
                #print(datex)
                datevector = datex.split()
                dayx = datevector[1]
                monthx = datevector[0]
                monthx = monthx.lower()
                yearx = datevector[2]
                #print(dayx, monthx, yearx)
                month3 = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
                indexm = month3.index(monthx)
                article_date = datetime(int(yearx),int(indexm+1),int(dayx))
                #print(article_date)
                hold_dict['date_publish'] = article_date 
            except:  
                hold_dict['date_publish'] = None

    return hold_dict 


## Process to extract urls from Wayback and then scrape them using Newsplease:
for source in sources:
    # Querying the web archive database for the specified sources in the specified period:
    url = "https://web.archive.org/cdx/search/cdx?url=" + source + "&matchType=domain&collapse=urlkey&from=" + fromdate + "&to=" + todate + "&output=json"
    print("Working on ", source)
    
    urls = rq.get(url).text
    parse_url = json.loads(urls) #parses the JSON from urls.

    ## Extracts timestamp and original columns from urls and compiles a url list.
    url_list = []
    for i in range(1,len(parse_url)):
        orig_url = parse_url[i][2]
        tstamp = parse_url[i][1]
        waylink = tstamp+'/'+orig_url
        ## Compiles final url pattern:
        final_url = 'https://web.archive.org/web/' + waylink
        url_list.append(final_url)

        ## SCRAPING WAYBACK URLS USING NEWSPLEASE:
        try:
            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            response = requests.get(final_url, headers=header)
            # process
            article = NewsPlease.from_html(response.text, url=final_url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "wayback_alt"
            article['source_domain'] = "elsalvador.com"
            # insert into the db
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'articles-{year}-{month}'
            except:
                colname = 'articles-nodate'

            # maintext:
            if article['maintext'] == None:
                soup = BeautifulSoup(response.text, 'html.parser')
                newurl = soup.find("p", {"class":"code shift target"})
                req = requests.get(url, headers = header)
                #soup = BeautifulSoup(req.content, 'html.parser')
                soup = BeautifulSoup(req.text, 'html.parser')
                article['maintext'] = elsalvadorcom_story(soup)['maintext']
                article['url'] = newurl

            try:
                #myquery = { "url": final_url, "source_domain" : 'web.archive.org'}
                #db[colname].delete_one(myquery)
                db[colname].insert_one(article)
                print("Inserted! in ", colname)
                #db['urls'].insert_one({'url': article['url']})
            except DuplicateKeyError:
                db[colname].insert_one(article)
                #print("DUPLICATE! deleting")
                print("DUPLICATE! but Inserted! in:", colname)

        except Exception as err: 
            print("ERRORRRR......", err)
            pass

    print("Done with ", len(url_list), "urls from ",  source)

# List of unique urls:
list_urls = list(set(url_list))

## INSERTING IN THE DB:
url_count = 0
for url in list_urls:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if "elsalvador.com" in url:
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
                    article['source_domain'] = "elsalvador.com"
                    
                    ## Fixing Date:
                    #soup = BeautifulSoup(response.content, 'html.parser')

                    #try:
                    #    contains_date = soup.find("div", {"class":"post-meta-date"}).text
                        #contains_date = soup.find("i", {"class":"fa fa-calendar"}).text
                    #    article_date = dateparser.parse(contains_date, date_formats=['%d/%m/%Y'])
                    #    article['date_publish'] = article_date
                    #except:
                    #    article_date = article['date_publish']
                    #    article['date_publish'] = article_date

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
                        #print(article['date_publish'].month)
                        #print(article['title'][0:200])
                        #print(article['maintext'][0:200])
                        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        print("DUPLICATE! Not inserted.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
            else:
                pass


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")