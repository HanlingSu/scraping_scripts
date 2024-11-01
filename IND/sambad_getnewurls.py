#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on oct 4 2023

@author: togbedji

This script updates sambad.com using daily sitemaps
It can be run as often as one desires. 

Sitemaps: (going back to 2021)
https://dainiknavajyoti.com/sitemap.xml
https://dainiknavajyoti.com/sitemaps/post-display_1.xml
https://dainiknavajyoti.com/sitemaps/post-display_5.xml
https://dainiknavajyoti.com/news-sitemap.xml
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

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## NEED TO DEFINE SOURCE!
source = 'sambad.in'

########################################
##            Custom parser           ##   
########################################
def sambad_story(soup):
    """
    Function to pull the information we want from indiatimes.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}

    # Get Title:
    try:
        #article_title = soup.find("title").text
        #divText = soup.find("h1", {"class":"single-post-title"})
        article_title = soup.find("h1", {"class":"single-post-title"}).text
        hold_dict['title']  = article_title

    except:
        article_title = None
        hold_dict['title']  = None

    # Get Main Text:
    try:
        maintext_contains = soup.find("div", {"class":"entry-content clearfix single-post-content"}).text
        hold_dict['maintext'] = maintext_contains
    except:
        maintext = None
        hold_dict['maintext']  = None

    # Get Date:
    try:
        date_contains = soup.find("time", {"class":"post-published updated"}).text.replace("Last updated ","")
        date = dateparser.parse(date_contains, date_formats=['%d/%m/%Y'])
        hold_dict['date_publish'] = date
    except:
        hold_dict['date_publish'] = None

    return hold_dict
########################################

for i in range(206,195, -1):
    ## COLLECTING URLS
    urls = []
    ## COLLECTING DATES
    dates = []

    sitemap = "https://sambad.in/wp-sitemap-posts-post-" + str(i) + ".xml"
    print("Extracting from: ", sitemap)

    reqs = requests.get(sitemap, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    for link in soup.findAll('loc'):
        urls.append(link.text)
    
    for datex in soup.findAll('lastmod'):
        dates.append(datex.text)

    # Scrape:
    for url in urls:
        if url == "":
            pass
        else:
            if url == None:
                pass
            else:
                if 'sambad.in' in url:
                    print("+ URL: ", url)
                    urlindex = urls.index(url)
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
                        article['source_domain'] = 'sambad.in'
                        
                        ## Fixing Date, Title, and Text
                        soup = BeautifulSoup(response.content, 'html.parser')

                        # Title:
                        article['title'] = sambad_story(soup)['title']

                        # Text:
                        article['maintext'] = sambad_story(soup)['maintext']

                        # Date: 
                        article['date_publish'] = sambad_story(soup)['date_publish']

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
                            #print(article['date_publish'])
                            #print(article['date_publish'].month)
                            print("+ TITLE: ", article['title'][0:80])
                            print("+ TEXT: ", article['maintext'][0:100])
                            print("+ DATE: ", article['date_publish'])
                            print("+ Inserted in ", colname, " - number of urls so far.")
                        except DuplicateKeyError:
                            print("DUPLICATE! Not inserted.")
                    except Exception as err: 
                        print("ERRORRRR......", err)
                        pass
                else:
                    pass


    print("Done inserting manually collected urls")





