#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 19 2023

@author: Rethis 

 www.sakshi.com
 
"""
# Packages:
import time
import random
import sys
sys.path.append('../')
import os
import re
#pip install p_tqdm
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
import dateutil.parser


import math

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## NEED TO DEFINE SOURCE!
source = 'sakshi.com'

#################
# Custom Parser #
def sakshi_story(soup):
    """
    Function to pull the information we want from indiatimes.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    
    # Get Title: 
    try:
        #article_title = soup.find("title").text
        article_title = soup.find("h1", {"id":"page-title"}).text
        hold_dict['title']  = article_title   

    except:
        article_title = None
        hold_dict['title']  = None
        
    # Get Main Text:
    try: 
        maintext_contains = soup.find("p", {"class":"rtejustify"}).text
        #maintext_contains = soup.find("h1", {"class":"malayalam "}).text
        #maintext = maintext_contains['content']
        hold_dict['maintext'] = maintext_contains
    except: 
        maintext = None
        hold_dict['maintext']  = None

    # Get Date:
    try: 
        date_contains = soup.find("div", {"class":"submitted"}).text
        date_extract = date_contains.replace("Updated :", "")
        date_extract = date_extract.split('|')[0]
# Extract date part using regular expressions
        date_pattern = r"(\w{3}\s\d{1,2},\s\d{4})"
        match = re.search(date_pattern, date_extract)
        if match:
            date_str = match.group(1)
            parsed_date = dateutil.parser.parse(date_str)
        else:
            print("Date not found in the expected format.")
        hold_dict['date_publish'] = parsed_date
    except: 
        hold_dict['date_publish'] = None

    return hold_dict 
##
#################


# STEP 0: Get sitemap urls:
siteurls = []

url = "https://www.sakshi.com/sitemap.xml"
print("Extracting from: ", url)
reqs = requests.get(url, headers=headers)
soup = BeautifulSoup(reqs.text, 'html.parser')
for link in soup.findAll('loc'):
    siteurls.append(link.text)

#for link in soup.find_all('a'):
#    urls.append(link.get('href')) 

#dftest = pd.DataFrame(siteurls)  
#dftest.to_csv('/Users/diegoromero/Downloads/test.csv')  
print("Number of sitemaps found: ", len(siteurls))


# STEP 1: Get urls of articles from sitemaps:
# STEP 1: Get urls of articles from sitemaps:
for sitmp in siteurls:
    urls = []
    print("Extracting from: ", sitmp)
    reqs = requests.get(sitmp, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    #for link in soup.findAll('loc'):
    #    urls.append(link.text)
    for link in soup.find_all('a'):
        urls.append(link.get('href')) 
    print("URLs so far: ", len(urls))

    # Manually check urls:
    #dftest = pd.DataFrame(list_urls)  
    #dftest.to_csv('/Users/diegoromero/Downloads/test.csv')  

    # STEP 2: Get rid or urls from blacklisted sources

    Nurls = []
    blacklisted = [None, '/', '/video/live', 'https://epaper.sakshi.com/', 'https://www.sakshipost.com', 'https://education.sakshi.com/', '/ysr', 'https://www.sakshi.com/careers', 'https://www.sakshi.com/video/live', 'http://facebook.com/sakshinews', 'http://twitter.com/sakshinews', 'https://www.instagram.com/sakshinews/', 'http://www.youtube.com/user/sakshinews', 'https://t.me/SakshiDailyNews', '/archive', 'https://www.kooapp.com/profile/sakshinews', 'https://www.linkedin.com/company/sakshimedia', 'javascript:void(0);', '/']
    web = '.com'
    for link in urls:
        if link != None:
            if link not in blacklisted:
                if web not in link:
                    Nlink = 'https://www.sakshi.com' + link
                    Nurls.append(Nlink)

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
                if "sakshi.com" in url:
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
                        article['title'] = sakshi_story(soup)['title']

                        # Main Text
                        article['maintext'] = sakshi_story(soup)['maintext']

                        # Date of Publication
                        article['date_publish'] = sakshi_story(soup)['date_publish']

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












date_contains = "Updated: Mar 22, 2024, 18:55 IST | Created:"
date_extract = date_contains.replace("Updated :","")
date_extract = date_extract.split('|')[0]
#date_contains = soup.find("meta", {"itemprop":"datePublished"})
#date = date_contains['content']
parsed_date = dateutil.parser.parse(date_extract)
parsed_date