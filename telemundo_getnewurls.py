#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Feb 3 2021

@author: diegoromero

This script updates telemundo.com using sitemaps.

It can be run as often as one desires. 
"""
# Packages:
import random
import sys
from xml.dom import xmlbuilder
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


## Custom scraper:
def telemundocom_story(soup):
    """
    Function to pull the information we want from telemundo.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    #meta property="og:title" content="Au Niger, l’escalade macabre de l’Etat islamique"
    # Get Title: 
    try:
        #article_title = soup.find("title").text
        contains_title = soup.find("meta", {"property":"og:title"})
        article_title = contains_title['content']
        hold_dict['title']  = article_title   

    except:
        article_title = None
        hold_dict['title']  = None
        
    # Get Main Text:
    try:
        #contains_maintext = soup.find("meta", {"name":"description"})
        #maintext = contains_maintext['content']
        #maintext = soup.find("p").text
        maintext = soup.find("p", {"class":""}).text
        hold_dict['maintext'] = maintext
    except: 
        try: 
          maintext = soup.find("p", {"class":"endmarkEnabled"}).text
          hold_dict['maintext'] = maintext
        except: 
          maintext = None
          hold_dict['maintext']  = None

    # Get Date
    try:
        #meta data-test="timestamp__datePublished--meta" itemprop="datePublished" content="2021-01-31T15:00:00.000Z"
        contains_date = soup.find("meta", {"itemprop":"datePublished"})
        #contains_date = soup.find("meta", {"property":"article:published"})
        #article_date = contains_date['content']
        article_date = dateparser.parse(contains_date['content'])
        hold_dict['date_publish'] = article_date  

    except:
        article_date = None
        hold_dict['date_publish'] = None  
   
    return hold_dict 




# db connection:
db = MongoClient('mongodb://ml4pAdmin:ml4peace@research-devlab-mongodb-01.oit.duke.edu').ml4p

source = 'telemundo.com'

### EXTRACTING ulrs from sitemaps:
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

urls = []

# Define Pages:
page_0 = 1
page_1 = 9
pageslist = list(range(page_0, page_1))

# Sitemaps:
for pagex in pageslist:
    url = "https://www.telemundo.com/sitemap.xml?page=" + str(pagex)
    print("Obtaining URLs from this sitemap: ", url)

    try: 
        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        for link in soup.findAll('loc'):
            urls.append(link.text)
    except:
        pass

    print("+ URLs so far: ", len(urls))
    


# KEEP ONLY unique URLS:
dedupurls = list(set(urls))

# STEP 1: Get rid or urls from blacklisted sources
blpatterns = ['/2010/','/2011/','/2012/','/2013/','/2014/','/2015/','/2016/','/2017/','/2018/','/2019/','/2020/','/temporada/','/show/','/shows/', '/entretenimiento/', '/talentos/', '/series-y-novelas/', '/amp-video/', '/clima/', 'curiosidades/', '/alexa/', 'deportes/', '/deportes-show/', '/horoscopos/', '/religion/']

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
            except:
                pass

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
            if 'telemundo.com' in url:
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
                    article['source_domain'] = 'telemundo.com'
                    
                    ## Fixing what needs to be fixed:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    # Date:
                    if "/video/" in url:
                        ## Fixing main text
                        contains_all = soup.find("p", {"class":"video-details__dek-text"}).text
                        article['maintext'] = contains_all

                        ## Fixing Date
                        months = ["En","Feb","Mar","Ab","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
                        dateportion = contains_all[len(contains_all)-15:]

                        for month in months:
                            if month in dateportion:
                                monthx = months.index(month) + 1
                                dayindex = dateportion.find(",")
                                containsday = dateportion[dayindex-3:dayindex]
                                containsday = containsday.replace(".","")
                                containsday = containsday.replace(",","")
                                containsday = containsday.replace(" ","")
                                dayx = int(containsday)
                                yearx = dateportion[len(dateportion)-5:]
                                yearx = yearx.replace(".","")
                                yearx = yearx.replace(" ","")
                                yearx = int(yearx)
                                #dateextracted = datetime(int(yearx),int(monthx),int(dayx))
                                article['date_publish'] = datetime(int(yearx),int(monthx),int(dayx))
                                break
                            else:
                                #dateextracted = None
                                article['date_publish'] = None
                    else:
                        # DATE
                        try:
                            article['date_publish'] = telemundocom_story(soup)['date_publish']
                        except:
                            articledate = article['date_publish']
                            article['date_publish'] = articledate

                        # TITLE
                        try:
                            article['title'] = telemundocom_story(soup)['title']
                        except:
                            articletitle = article['title']
                            article['title'] = articletitle

                        # MAIN TEXT
                        try:
                            article['maintext'] = telemundocom_story(soup)['maintext']
                        except:
                            articlemaintext = article['maintext']
                            article['maintext'] = articlemaintext

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
                        #print(article['title'])
                        print("+TITLE: ", article['title'][0:20], " +MAIN TEXT: ", article['maintext'][0:25])
                        print("Date extracted: ", article['date_publish'], " + Inserted! in ", colname, " - number of urls so far: ", url_count)
                        db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        print("DUPLICATE! Not inserted.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
            else:
                pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")