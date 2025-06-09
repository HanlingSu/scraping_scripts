#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 20, 2022

@author: diegoromero

This script updates '168.am' using sitemaps.

It can be run as often as one desires. 
"""
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

source = '168.am'

### EXTRACTING ulrs from sitemaps:
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## CHANGE: initial and final sitemaps:
# 1. armenian
initialsitemap = 266
finalsitemap = 278

# 2. english
initialsitemap_en = 6
finalsitemap_en = 6

# 1. russian
initialsitemap_ru = 5
finalsitemap_ru = 5


# opinion_base = 'https://168.am/section/opinion/'
# for p in range(1, 15):
#     url = opinion_base + 'page/' +str(p)
#     response = requests.get(url, verify=False)
#     soup = BeautifulSoup(response.content)
#     for i in soup.find_all('div', {'class' : 'realated-item clearfix'}):
#         list_urls.append(i.find('a')['href'])

# Scraping from sitemaps -- ARMENIAN
for j in range(initialsitemap,finalsitemap+1):
    # to keep urls:
    urls = []

    # URL of the sitemap to scrape:
    url = 'https://168.am/wp-sitemap-posts-post-' + str(j) + '.xml'

    print("First Sitemap: ", url)

    reqs = requests.get(url, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    for link in soup.findAll('loc'):
        urls.append(link.text)
    #for link in soup.find_all('a'):
    #    urls.append(link.get('href')) 

    print("Obtained ", len(urls), " URLs from sitemap number ",str(j))

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
                if '168.am' in url:
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
                        article['source_domain'] = '168.am'
                        article['language'] = 'hy'
                        
                        ## Fixing what needs to be fixed:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Get Main Text:
                        if article['maintext'] == None:
                            try:
                                maintext =soup.find("div", {"class":"single-content-wrapper"}).text
                                article['maintext'] = maintext
                            except:
                                try:
                                    contains_maintext = soup.find("meta", {"property":"og:description"})
                                    maintext = contains_maintext['content']
                                    article['maintext'] = maintext  
                                except: 
                                    maintext = None
                                    article['maintext']  = None

                        
                        ## Fixing Date:      168.am
                        indexam = url.index("168.am")
                        yearstr = url[indexam+7:indexam+11]
                        monthstr = url[indexam+12:indexam+14]
                        daystr = url[indexam+15:indexam+17]

                        article_date = datetime(int(yearstr),int(monthstr),int(daystr))
                        article['date_publish'] = article_date

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



#############################################################################

# Scraping from sitemaps -- ENGLISH
for j in range(initialsitemap_en,finalsitemap_en+1):
    # to keep urls:
    urls = []

    # URL of the sitemap to scrape:
    url = 'https://en.168.am/wp-sitemap-posts-post-' + str(j) + '.xml'

    print("First Sitemap: ", url)

    reqs = requests.get(url, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    for link in soup.findAll('loc'):
        urls.append(link.text)
    #for link in soup.find_all('a'):
    #    urls.append(link.get('href')) 

    urls = urls[-200:]
    print("Obtained ", len(urls), " URLs from sitemap number ",str(j)," (ENGLISH)")

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

    print("Obtained ", len(list_urls), " USABLE URLs from sitemap number ",str(j)," (ENGLISH)")


    ## INSERTING IN THE DB:
    url_count = 0
    for url in list_urls:
        if url == "":
            pass
        else:
            if url == None:
                pass
            else:
                if '168.am' in url:
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
                        article['source_domain'] = '168.am'
                        article['language'] = 'en'
                        
                        ## Fixing what needs to be fixed:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Get Main Text:
                        if article['maintext'] == None:
                            try:
                                maintext =soup.find("div", {"class":"single-content-wrapper"}).text
                                article['maintext'] = maintext
                            except:
                                try:
                                    contains_maintext = soup.find("meta", {"property":"og:description"})
                                    maintext = contains_maintext['content']
                                    article['maintext'] = maintext  
                                except: 
                                    maintext = None
                                    article['maintext']  = None

                        
                        ## Fixing Date:     
                        indexam = url.index("168.am")
                        yearstr = url[indexam+7:indexam+11]
                        monthstr = url[indexam+12:indexam+14]
                        daystr = url[indexam+15:indexam+17]

                        article_date = datetime(int(yearstr),int(monthstr),int(daystr))
                        article['date_publish'] = article_date

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

    print("Done inserting ", url_count, " manually collected urls from sitemap number ", str(j), " (ENGLISH) of source ", source, " into the db.") 



#############################################################################

# Scraping from sitemaps -- RUSSIAN
for j in range(initialsitemap_ru,finalsitemap_ru+1):
    # to keep urls:
    urls = []

    # URL of the sitemap to scrape:
    url = 'https://ru.168.am/wp-sitemap-posts-post-' + str(j) + '.xml'

    print("First Sitemap: ", url)

    reqs = requests.get(url, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    for link in soup.findAll('loc'):
        urls.append(link.text)
    #for link in soup.find_all('a'):
    #    urls.append(link.get('href')) 

    print("Obtained ", len(urls), " URLs from sitemap number ",str(j)," (RUSSIAN)")

    # KEEP ONLY unique URLS:
    # urls = urls[-100:]

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

    print("Obtained ", len(list_urls), " USABLE URLs from sitemap number ",str(j)," (RUSSIAN)")


    ## INSERTING IN THE DB:
    url_count = 0
    for url in list_urls:
        if url == "":
            pass
        else:
            if url == None:
                pass
            else:
                if '168.am' in url:
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
                        article['source_domain'] = '168.am'
                        article['language'] = 'ru'
                        
                        ## Fixing what needs to be fixed:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Get Main Text:
                        if article['maintext'] == None:
                            try:
                                maintext =soup.find("div", {"class":"single-content-wrapper"}).text
                                article['maintext'] = maintext
                            except:
                                try:
                                    contains_maintext = soup.find("meta", {"property":"og:description"})
                                    maintext = contains_maintext['content']
                                    article['maintext'] = maintext  
                                except: 
                                    maintext = None
                                    article['maintext']  = None

                        
                        ## Fixing Date:     
                        indexam = url.index("168.am")
                        yearstr = url[indexam+7:indexam+11]
                        monthstr = url[indexam+12:indexam+14]
                        daystr = url[indexam+15:indexam+17]

                        article_date = datetime(int(yearstr),int(monthstr),int(daystr))
                        article['date_publish'] = article_date

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

    print("Done inserting ", url_count, " manually collected urls from sitemap number ", str(j), " (RUSSIAN) of source ", source, " into the db.") 