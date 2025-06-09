#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on April 29, 2022

@author: diegoromero

This script updates diario.elmundo.sv scraping urls from sections.

It can be run as often as one desires. 
 
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
uri = 'mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true'
db = MongoClient(uri).ml4p

# headers for scraping
#headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15'}

## COLLECTING URLS
urls = []

def diarioelmundosv_story(soup):
    """
    Function to pull the information we want from diario.elmundo.sv stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    
    # Get Title: 
    try:
        contains_title = soup.find("meta", {"property":"og:title"})
        article_title = contains_title['content']
        hold_dict['title']  = article_title.strip()   

    except:
        article_title = None
        hold_dict['title']  = None
        
    # Get Main Text:
    try:
        contains_maintext = soup.find("meta", {"property":"og:description"})
        article_maintext = contains_maintext['content']
        hold_dict['maintext'] = article_maintext.strip()
        #
        #maintext_contains = soup.findAll("p")
        #maintext = maintext_contains[2].text + " " + maintext_contains[3].text
        #hold_dict['maintext'] = maintext
    except: 
        maintext = None
        hold_dict['maintext']  = None

    # Get Date
    try:  
        contains_date = soup.find("meta", {"property":"article:published_time"})
        article_date = contains_date['content']
        #article_date = dateparser.parse(article_date,date_formats=['%d/%m/%Y'])
        article_date = dateparser.parse(article_date)
        hold_dict['date_publish'] = article_date  
    except:
        hold_dict['date_publish'] = None
   
    return hold_dict 

## NEED TO DEFINE SOURCE!
source = 'diario.elmundo.sv'


#https://diario.elmundo.sv/morearticles/politica
#https://diario.elmundo.sv/morearticles/politica?pgno=1140
#https://diario.elmundo.sv/morearticles/economia
#https://diario.elmundo.sv/morearticles/economia?pgno=590
#https://diario.elmundo.sv/morearticles/nacionales
#https://diario.elmundo.sv/morearticles/nacionales?pgno=1563
#https://diario.elmundo.sv/morearticles/el-mundo
#https://diario.elmundo.sv/morearticles/el-mundo?pgno=1025

## STEP 0: Define sections and max pages. 
sections = ['politica','economia','nacionales','el-mundo']
# CHANGE endnumbers for each section in accordance with how far 
# back you need to go:
#endnumber = ['1140','590','1563','1024']
endnumber = ['30','28','60','60']
# endnumber = ['50','30','80','63']

for section in sections:
    indexword = sections.index(section)
    endnumberx = endnumber[indexword]

    for i in range(1, int(endnumberx)+1):
        if i == 1:
            url = "https://diario.elmundo.sv/morearticles/" + section  
        else:
            url = "https://diario.elmundo.sv/morearticles/" + section + "?pgno=" + str(i)
        
        print("Section: ", section, " -> URL: ", url)

        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        for link in soup.find_all('div', {'class' : 'article-title'}):
            urls.append(link.find('a')['href']) 
        print("URLs so far: ", len(urls))

# STEP 1: Get rid or urls from blacklisted sources
blpatterns = ['/editorial/','/opinion/','/deportes/']

# List of unique urls:
dedup = list(set(urls))
list_urls = []
for url in dedup:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            try: 
                if "diario.elmundo.sv" in url:
                    count_patterns = 0
                    for pattern in blpatterns:
                        if pattern in url:
                            count_patterns = count_patterns + 1
                    if count_patterns == 0:
                        #newurl = "https://www.bd-pratidin.com/" + url 
                        list_urls.append(url)
            except:
                pass



# Manually check urls:
#list_urls = list(set(urls))
#dftest = pd.DataFrame(list_urls)  
#dftest.to_csv('/Users/diegoromero/Downloads/test.csv')  
print("Total number of USABLE urls found: ", len(list_urls))


## INSERTING IN THE DB:
url_count = 0
for url in list_urls:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if "diario.elmundo.sv" in url:
                print(url, "FINE")
                ## SCRAPING USING NEWSPLEASE:
                try:
                    #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
                    #header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15'}

                    response = requests.get(url, headers=header)
                    # process
                    article = NewsPlease.from_html(response.text, url=url).__dict__
                    # add on some extras
                    article['date_download']=datetime.now()
                    article['download_via'] = "Direct2"
                    article['source_domain'] = "diario.elmundo.sv"
                    article['language'] = 'es'
                    
                    ## Fixing what needs to be fixed:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # TITLE:
                    if article['title'] == None:
                        article['title'] = diarioelmundosv_story(soup)['title']
                    
                    # Main Text:
                    if article['maintext'] == None:
                        article['maintext'] = diarioelmundosv_story(soup)['maintext']

                    # Date:
                    article['date_publish'] = diarioelmundosv_story(soup)['date_publish']
                    print("Date -- ", article['date_publish'])  
                    #print("Date -- ", diarioelmundosv_story(soup)['date_publish'])  


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
                        print("Title:", article['title'][0:15], " + Main Text : ",article['maintext'][0:40])
                        #print("TEXT: ", article['maintext'])
                        print("Date extracted: ", article['date_publish'], " + Inserted! in ", colname, " - number of urls so far: ", url_count)
                        #db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        #myquery = { "url": url}
                        #db[colname].delete_one(myquery)
                        # Inserting article into the db:
                        #db[colname].insert_one(article)
                        # count:
                        #url_count = url_count + 1
                        #print(" + Rescraping DUPLICATE -- Date extracted: ", article['date_publish'], " + Inserted! in ", colname, " - number of urls so far: ", url_count)
                        #db['urls'].insert_one({'url': article['url']})
                        print("DUPLICATE! Not inserted.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
            else:
                pass


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")