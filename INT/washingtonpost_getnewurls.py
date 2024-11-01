#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Nov 11 2021

@author: diegoromero

This script updates washingtonpost.com using section sitemaps.
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
#db = MongoClient('mongodb://ml4pAdmin:ml4peace@research-devlab-mongodb-01.oit.duke.edu').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


## NEED TO DEFINE SOURCE!
source = 'washingtonpost.com'
list_urls = pd.read_csv('Downloads/peace-machine/peacemachine/getnewurls/INT/washington.csv')['0']
#https://www.washingtonpost.com/arcio/sitemap/master/index/

# STEP 0: Get sitemap urls:
# Note: washingtonpost.com has section sitemaps. There are 250 urls per sitemap,
#       and the first one offset=0 ALWAYS has the most recent articles.

# ## Need to define number of pages!
# sections = ["politics","world","coronavirus","technology","business","climate-environment","investigation","climate","national","national-security","local"]
# nombpages = ["10","5","5","5","5","5","5","5","5","5","5"] #CHANGE

# #https://www.washingtonpost.com/arcio/sitemap/story/news/?size=250&offset=250

# ## TOPICS 
# for word in sections:
#     ## COLLECTING URLS
#     urls = []
#     indexword = sections.index(word)
#     endnumberx = nombpages[indexword]

#     for i in range(0, int(endnumberx)+1):
#         #offsetnumb = i
#         offsetnumb = i*250
#         url = "https://www.washingtonpost.com/arcio/sitemap/" + word + "/?size=250&offset=10" + str(offsetnumb)
#         print("Extracting from sitemap: ", url)
#         reqs = requests.get(url, headers=headers)
#         soup = BeautifulSoup(reqs.text, 'html.parser')
#         for link in soup.findAll('loc'):
#             urls.append(link.text)
#         urls = list(set(urls))
#         print("URLs so far: ",len(urls))

#     #dftest = pd.DataFrame(urls)  
#     #dftest.to_csv('/Users/diegoromero/Downloads/test.csv')  


#     # STEP 2: Get rid or urls from blacklisted sources
#     blpatterns = ['/sports/', '/entertainment/', '/food/', '/health/', '/lifestyle/', '/obituaries/', '/weather/', '/opinions/', '/arts-entertainment/', '/outlook/', '/creativegroup/', '/post-opinion/', '/goingoutguide/', '/movies/', '/history/', '/olympics/', '/podcasts/', '/religion/', '/science/', '/travel/', '/video/']

#     clean_urls = []
#     for url in urls:
#         if url == None:
#             pass
#         else:
#             if url == "":
#                 pass
#             else:
#                 if "2024" in url:
#                     if "washingtonpost.com" in url:
#                             count_patterns = 0
#                             for pattern in blpatterns:
#                                 if pattern in url:
#                                     count_patterns = count_patterns + 1
#                             if count_patterns == 0:
#                                 clean_urls.append(url)
#                     else:
#                         indexd = url.index("/")
#                         if indexd == 0:
#                             newurl = "https://www.washingtonpost.com" + url 
#                             clean_urls.append(newurl)
#                 else:
#                     pass
#     # List of unique urls:
#     list_urls = list(set(clean_urls))

#     print("Total number of USABLE urls found: ", len(list_urls)," for - ",word)


## INSERTING IN THE DB:
url_count = 0
for url in list_urls:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if "washingtonpost.com" in url:
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
                        #print(article['date_publish'])
                        #print(article['title'])
                        #print(article['maintext'])
                        print("Inserted! in ", colname, " - number of urls so far: ", url_count, " out of ", len(list_urls), " + word: ", word)
                        db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        print("DUPLICATE! Not inserted.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
            else:
                pass


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db. - keyword: ", word)