#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Jan 12 2024

@author: Rethis 

 www.asomiyapratidin.in
 
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

import math

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## NEED TO DEFINE SOURCE!
source = 'asomiyapratidin.in'

#################
# Custom Parser #
def asomiyapratidin_story(soup):
    """
    Function to pull the information we want from indiatimes.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    
    # Get Title: 
    try:
        #article_title = soup.find("title").text
        article_title = soup.find("h1", {"class":"arr--story--headline-h1 story-headline-m_headline__x10-O story-headline-m_dark__1_kPz"}).text
        hold_dict['title']  = article_title   

    except:
        article_title = None
        hold_dict['title']  = None
        
    # Get Main Text:
    try: 
        maintext_contains = soup.find("div", {"class":"arrow-component arr--text-element text-m_textElement__e3QEt text-m_dark__1TC18"}).text
        #maintext_contains = soup.find("h1", {"class":"malayalam "}).text
        #maintext = maintext_contains['content']
        hold_dict['maintext'] = maintext_contains
    except: 
        maintext = None
        hold_dict['maintext']  = None

    # Get Date:
    try: 
        div_tag = soup.find("div", class_="publish-details-m_date__3ZIQN")
# Extract the value of the "datetime" attribute from the <time> tag
        time_tag = div_tag.find("time")
        date = time_tag["datetime"]
        date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
        hold_dict['date_publish'] = date
    except: 
        hold_dict['date_publish'] = None

    return hold_dict 
##
#################


# STEP 0: Get sitemap urls:
siteurls = []

url = "https://www.asomiyapratidin.in/sitemap.xml"
print("Extracting from: ", url)
reqs = requests.get(url, headers=headers)
soup = BeautifulSoup(reqs.text, 'html.parser')
for link in soup.findAll('loc'):
    siteurls.append(link.text)
  
print("Number of sitemaps found: ", len(siteurls))




# STEP 1: Get urls of articles from sitemaps:
for sitmp in siteurls:
    urls = []
    print("Extracting from: ", sitmp)
    reqs = requests.get(sitmp, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    for link in soup.findAll('loc'):
        urls.append(link.text)
    #for link in soup.find_all('a'):
      #  urls.append(link.get('href')) 
    print("URLs so far: ", len(urls))


    Nurls = []
    blacklisted = [None, '/', '/sports', '/entertainment', '/lifestyle', '/health', '/my-opinion']
    web = 'asomiyapratidin.in'
    for link in urls:
        if link != None:
            if link not in blacklisted:
                Nurls.append(link)

    # List of unique urls:
    list_urls = list(set(Nurls))

    print("Total number of USABLE urls found: ", len(list_urls))
    #time.sleep(30)

    ## INSERTING IN THE DB:
    url_count = 0
    for url in list_urls:
        if url == "":
            pass
        else:
            if url == None:
                pass
            else:
                if "asomiyapratidin.in" in url:
                    ## SCRAPING USING NEWSPLEASE:
                    try:
                        # count:
                        url_count = url_count + 1
                        #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
                        header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                        response = requests.get(url, headers=header)
                        # process
                        article = NewsPlease.from_html(response.text, url=url).__dict__
                        # add on some extras
                        article['date_download']=datetime.now()
                        article['download_via'] = "Direct2"
                        article['source_domain'] = source

                        
                        ## Fixing main texts when needed:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Title:
                        article['title'] = asomiyapratidin_story(soup)['title']

                        # Main Text
                        article['maintext'] = asomiyapratidin_story(soup)['maintext']

                        # Date of Publication
                        article['date_publish'] = asomiyapratidin_story(soup)['date_publish']

                        # Get Main Text:
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
                            print("+ URL: ",url)
                            print("+ DATE: ",article['date_publish'].month)
                            print("+ TITLE: ",article['title'][0:200])
                            print("+ MAIN TEXT: ",article['maintext'][0:200])
                            print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                            pogressm = url_count/len(list_urls)
                            print(" --> Progress:", str(pogressm), " -- Sitemamp: ", sitmp)
                            db['urls'].insert_one({'url': article['url']})
                        except DuplicateKeyError:
                            pogressm = url_count/len(list_urls)
                            print("DUPLICATE! Not inserted. --> Progress:", str(pogressm), " -- Sitemamp: ", sitmp)
                    except Exception as err: 
                        print("ERRORRRR......", err)
                        #pass
                else:
                    pass


    print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db. Now waiting 63 seconds...")
    time.sleep(3)









