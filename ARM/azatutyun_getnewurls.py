#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 20, 2022

@author: diegoromero

This script updates 'azatutyun.am' using (zipped) sitemaps.
https://www.azatutyun.am/sitemap.xml

It can be run as often as one desires. 
"""

import requests
import gzip
import io as io
from io import StringIO ## for Python 3
# Packages:
import random
import sys
sys.path.append('../')
import os
import re
#from p_tqdm import p_umap
#from tqdm import tqdm
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
from bs4 import BeautifulSoup
# %pip install dateparser
import dateparser
import pandas as pd


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'azatutyun.am'

### EXTRACTING ulrs from sitemaps:
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
#headers = {'User-Agent': 'MLP Bot'}

## CHANGE: initial and final sitemaps
initialsitemap = 1
finalsitemap = 1

def azatutyunam_story(soup):
    """
    Function to pull the information we want from azatutyun.am stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    
    # Get Title:
    try:
        contains_title = soup.find("meta", {"name":"title"})
        title = contains_title['content']
        hold_dict['title'] = title
    except:
        try:
            title = soup.find("meta", {"property":"og:title"})["content"] 
            hold_dict['title'] = title
        except:
            try: 
                title = soup.find("title").text
                hold_dict['title'] = title
            except:
                hold_dict['title'] = None
        
    # Get Main Text:
    try:
        maintext = soup.find("div", {"class":"wsw"}).text
        hold_dict['maintext'] = maintext
    except:
        hold_dict['maintext']  = None

    # Get Date 
    try:
        contains_date = soup.find("time")['datetime']
        article_date = dateparser.parse(contains_date)
        hold_dict['date_publish'] = article_date
    except:
        hold_dict['date_publish'] = None

    return hold_dict 

# Scraping from sitemaps
for j in range(initialsitemap,finalsitemap+1):
    # to keep urls:
    urls = []

    # URL of the sitemap to scrape:
    url = "https://www.azatutyun.am/sitemap_16_" + str(j) + ".xml.gz"
    print("Scraping: ", url)

    r = requests.get(url, headers=headers)
    #sitemap = gzip.GzipFile(fileobj=io.StringIO(r.content)).read()
    #response = requests.get(sitemap, headers=headers)

    content = r.content
    text = gzip.decompress(content).decode('utf-8')

    #print(text)
    #reqs = requests.get(sitemap, headers=headers)
    soup = BeautifulSoup(text, 'html.parser')

    for link in soup.findAll('loc'):
        urls.append(link.text)
        print(link.text)
    #for link in soup.find_all('a'):
    #    urls.append(link.get('href')) 

    print("Obtained ", len(urls), " URLs from sitemap number ", str(j))

    # KEEP ONLY unique URLS:
    dedupurls = list(set(urls))

    # STEP 1: Get rid or urls from blacklisted sources
    blpatterns = ['/gallery/', '/tag/', '/author/', '/category/', '/tv_show/']

    list_urls = []
    for url in dedupurls:
        if url == "":
            pass
        else:
            if url == None:
                pass
            else:
                try: 
                    count_patterns = 0
                    for pattern in blpatterns:
                        if pattern in url:
                            count_patterns = count_patterns + 1
                    if count_patterns == 0:
                        list_urls.append(url)
                        #print(url)
                except:
                    pass

    print("Obtained ", len(list_urls), " USABLE URLs from sitemap number ",str(j))


    ## INSERTING IN THE DB:
    url_count = 0
    for url in list_urls:
        if url == "":
            pass
        else:
            if url == None:
                pass
            else:
                if 'azatutyun.am' in url:
                    print(url, "FINE")
                    ## SCRAPING USING NEWSPLEASE:
                    try:
                        #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
                        #header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                        header = {'User-Agent': 'MLP Bot'}
                        response = requests.get(url, headers=header)
                        # process
                        article = NewsPlease.from_html(response.text, url=url).__dict__
                        # add on some extras
                        article['date_download']=datetime.now()
                        article['download_via'] = "Direct2"
                        article['source_domain'] = 'azatutyun.am'
                        article['language'] = 'hy'
                        
                        ## Fixing what needs to be fixed:
                        soup = BeautifulSoup(response.content, 'html.parser')

                        # Get Title:
                        article['title'] = azatutyunam_story(soup)['title']
                        
                        # Get Main Text:
                        if article['maintext'] == None:
                            try:
                                article['maintext'] = azatutyunam_story(soup)['maintext']
                            except:
                                article['maintext']  = None

                        ## Fixing Date:
                        article['date_publish'] = azatutyunam_story(soup)['date_publish']

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
                            print(article['title'])
                            print(article['maintext'])
                            #print("+Title: ", article['title'][0:20]," +TEXT: ", article['maintext'][0:35])
                            print("Date extracted: ", article['date_publish'], " + Inserted! in ", colname, " - number of urls so far: ", url_count)
                            db['urls'].insert_one({'url': article['url']})
                        except DuplicateKeyError:
                            print("DUPLICATE! Not inserted.")
                    except Exception as err: 
                        print("ERRORRRR......", err)
                        pass
                else:
                    pass

    print("Done inserting ", url_count, " manually collected urls from sitemap number ", str(j), " of source ", source, " into the db.") 

















