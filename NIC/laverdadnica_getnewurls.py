#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Apr 2 2021

@author: diegoromero

This script updates 'laverdadnica.com' using section sitemaps.
You can run this script as often as you want.
 
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

# Custom Parser:
def laverdadnicacom_story(soup):
    """
    Function to pull the information we want from laverdadnica.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    # create a dictionary to hold everything in
    hold_dict = {}
    
    # Get Title: 
    try:
        article_title = soup.find("title").text
        hold_dict['title']  = article_title   

    except:
        hold_dict['title']  = None
        
    # Get Main Text:
    try:
        maintext = ''
        containstext = soup.find_all('p')
        for i in containstext[4:]:
            maintext += i.text
       
        #maintext = soup.find('p', attrs={'class':'entry-excerpt entry-excerpt-content-custom'}).text
        #soup.find("strong").text <p class="entry-excerpt entry-excerpt-content-custom">
        hold_dict['maintext'] = maintext

    except: 
        try:
            containstext = soup.find("meta", {"name": "description"})
            maintext = containstext['content']
            hold_dict['maintext'] = maintext 
        except:
            hold_dict['maintext']  = None

    # Get Date:
    #meta property="article:published_time" content="2022-04-02T16:26:32+00:00"
    try:
        contains_date = soup.find("meta", {"property": "article:published_time"})
        article_date = dateparser.parse(contains_date['content'])
        hold_dict['date_publish'] = article_date 
    except:
        try:
            contains_date = soup.find("meta", {"property": "og:updated_time"})
            article_date = dateparser.parse(contains_date['content'])
            hold_dict['date_publish'] = article_date 
        except:
            hold_dict['date_publish'] = None 
 

    return hold_dict  



## COLLECTING URLS
direct_URLs = []

## NEED TO DEFINE SOURCE!
source = 'laverdadnica.com'

# Custom Parser:


# STEP 0: Get sitemap urls:
# post-sitemap 
url = 'https://laverdadnica.com/post-sitemap0.xml'
print("Sitemap: ", url)

reqs = requests.get(url, headers=headers)
soup = BeautifulSoup(reqs.text, 'html.parser')
#print(soup)

for link in soup.findAll('loc'):
    print(link.text)
    direct_URLs.append(link.text)
#for link in soup.find_all('a'):
#    sitemaps.append(link.get('href')) 

print("direct_URLs: ", len(direct_URLs))

list_urls = direct_URLs.copy()[:100]

## INSERTING IN THE DB:
url_count = 0
processed_url_count = 0
for url in list_urls:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if 'laverdadnica.com' in url:
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
                    article['source_domain'] = 'laverdadnica.com'
                    
                    ## Fixing what needs to be fixed:
                    #soup = BeautifulSoup(response.content, 'html.parser')
                    response = requests.get(url, headers=header).text
                    soup = BeautifulSoup(response)

                    # TITLE:
                    if article['title'] == None:
                        try:
                            article['title'] = laverdadnicacom_story(soup)['title']
                        except:
                            article['title'] == None
                    print('newsplease title', article['title'])

                    # MAIN TEXT:
              
                    try:
                        article['maintext'] = laverdadnicacom_story(soup)['maintext']
                    except:
                        article['maintext'] == None

                    if  article['maintext']:
                        print('newsplease maintext', article['maintext'][:50])

                    # Fixing date:
                    article['date_publish'] = laverdadnicacom_story(soup)['date_publish']
                    print('newsplease date', article['date_publish'])
                    
                    #if article['date_publish'] == None:
                    #    article['date_publish'] = datetime(year,month,1)

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
                        if colname != 'articles-nodate':
                            url_count = url_count + 1
                            print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        else:
                            print("Inserted! in ", colname)
                        db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        myquery = { "url": url, "source_domain" : source}
                        db[colname].delete_one(myquery)
                        db[colname].insert_one(article)
                        print("DUPLICATE! Updated.")
                except Exception as err: 
                    print("ERRORRRR......", err)

                    pass
                processed_url_count += 1
                print('\n',processed_url_count, '/', len(list_urls), 'articles have been processed ...\n')

            else:
                pass


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")