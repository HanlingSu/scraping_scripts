#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Jan 12 2021

@author: diegoromero

This script updates enqueteplus.com using queries per section. 
This script can be ran whenever needed (just make the necessary modifications).
 
"""
# Packages:
import sys
sys.path.append('../')
from pymongo import MongoClient
from urllib.parse import urlparse
from datetime import datetime
from pymongo.errors import DuplicateKeyError
import requests
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


## Custom Parser
def enquetepluscom_story(soup):
    """
    Function to pull the information we want from enqueteplus.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    # Get Title: 
      
    # Get Date
    try: 
        months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        contains_date = soup.find("footer", {"class":"submitted"}).text
        contains_datelist = contains_date.split()
        dayn = int(contains_datelist[2])
        yearn = int(contains_datelist[4])
        monthn = months.index(contains_datelist[3]) + 1
        article_date = datetime(int(yearn),int(monthn),int(dayn))
        #article_date = dateparser.parse(article_date, date_formats=['%d/%m/%Y'])
        hold_dict['date_publish'] = article_date  

    except:
        article_date = None
        hold_dict['date_publish'] = None  
   
    return hold_dict 

## COLLECTING URLS
urls = []

## NEED TO DEFINE SOURCE!
source = 'enqueteplus.com'

# STEP 1: Extracting urls from key sections:
#sections = ['politique','social']
#number = ['2','2']

sections = ['politique','a','economie','international']
page_start = [15, 20, 4, 2]
page_end = [15, 20, 4, 2]
for sect, ps, pe in zip(sections, page_start, page_end) :
  
    for p in range(ps,pe+3):
       
        url = "https://www.enqueteplus.com/sections/" + sect + "?page=" + str(p)

        print("Extracting from ", url)

        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        for link in soup.find_all('h2', {'class' : 'node-title'}):
            try:
                urls.append(link.find('a')['href']) 
            except:
                pass
        print("+ Number of urls so far: ", len(urls))

# Manually check urls:
#dftest = pd.DataFrame(list_urls)  
#dftest.to_csv('/Users/diegoromero/Downloads/test.csv')  

# STEP 2: Get rid or urls from blacklisted sources
blpatterns = ['/wp-json/', '/photo/', ':80/', '/index.php/', '/wp-content/', '/images/','/category/', '?page=']

# List of unique urls:
dedup = list(set(urls))
list_urls = ['https://www.enqueteplus.com' + i for i in dedup]

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
            if "enqueteplus.com" in url:
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
                    article['source_domain'] = 'enqueteplus.com'
                    article['language'] = 'fr'
                    
                    ## Fixing Date, Main Text and Title:
                    response = requests.get(url, headers=header).text
                    soup = BeautifulSoup(response)

                    ## Title
                    #article['title'] = ferloocom_story(soup)['title'] 
                    ## Main Text
                    #article['maintext'] = ferloocom_story(soup)['maintext'] 
                    ## Date
                    article['date_publish'] = enquetepluscom_story(soup)['date_publish'] 

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
                        print(article['date_publish'])
                        print("Title: ", article['title'][0:25]," + Main Text: ", article['maintext'][0:30])
                        #print(article['maintext'])
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