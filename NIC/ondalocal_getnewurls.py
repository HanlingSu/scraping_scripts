#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Apr 2 2021

@author: diegoromero

This script updates 'ondalocalni.com' using section sitemaps.
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
def ondalocalnicom_story(soup):
    """
    Function to pull the information we want from ondalocalni.com stories
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
        containstext = soup.findAll('p')
        maintext = containstext[1].text + " " + containstext[2].text
        #maintext = soup.find('p', attrs={'class':'entry-excerpt entry-excerpt-content-custom'}).text
        #soup.find("strong").text <p class="entry-excerpt entry-excerpt-content-custom">
        hold_dict['maintext'] = maintext

    except: 
        hold_dict['maintext']  = None

    # Get Date:
    #meta property="article:published_time" content="2022-04-02T16:26:32+00:00"
    try:
        date = soup.find('meta', attrs={'itemprop':'datePublished'})['content']

        hold_dict['date_publish'] = dateparser.parse(date)
    except:
        article_date = None
        hold_dict['date_publish'] = None  

    return hold_dict 



## COLLECTING URLS
urls = []

## NEED TO DEFINE SOURCE!
source = 'ondalocalni.com'

# Custom Parser:


# STEP 0: Get sitemap urls:
# post-sitemap 
url = "https://ondalocalni.com/sitemap.xml"
print("Sitemap: ", url)

reqs = requests.get(url, headers=headers)
soup = BeautifulSoup(reqs.text, 'html.parser')

for link in soup.findAll('loc'):
    urls.append(link.text)

print("URLs so far: ", len(urls))


# # Step 1: URLs from the "noticias" section
# for i in range(1,20):
#     url = 'https://ondalocalni.com/noticias/?page=' + str(i)

#     print("URL: ", url)

#     reqs = requests.get(url, headers=headers)
#     soup = BeautifulSoup(reqs.text, 'html.parser')

#     for link in soup.find_all('a'):
#         urlbit = link.get('href')
#         newurl = "https://ondalocalni.com" + urlbit
#         urls.append(newurl) 
    
#     print("URLs so far: ", len(urls))

# # Step 1: URLs from the "elecciones" section
# for i in range(1,22):
#     url = 'https://ondalocalni.com/elecciones-2021/?page=' + str(i)

#     print("URL: ", url)

#     reqs = requests.get(url, headers=headers)
#     soup = BeautifulSoup(reqs.text, 'html.parser')

#     for link in soup.find_all('a'):
#         urlbit = link.get('href')
#         newurl = "https://Downloads/peace-machine/peacemachine/getnewurls/NIC/ondalocal_getnewurls.py.com" + urlbit
#         urls.append(newurl) 
    
#     print("URLs so far: ", len(urls))



# KEEP ONLY unique URLS:
dedupurls = urls[:300]

#dftest = pd.DataFrame(urls)  
#dftest.to_csv('/Users/diegoromero/Downloads/test.csv')  

# STEP 3: Get rid or urls from blacklisted sources
blpatterns = ['/galeria/', '/audios/', '/podcast/', '/opinion/', '/deportes/']

list_urls = []
for url in dedupurls:
    if "ondalocal" in url:
        count_patterns = 0
        for pattern in blpatterns:
            if pattern in url:
                count_patterns = count_patterns + 1
        if count_patterns == 0:
            list_urls.append(url)

print("Total number of USABLE urls found: ", len(list_urls))


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
            if 'ondalocal' in url:
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
                    article['source_domain'] = 'ondalocalni.com'
                    
                     ## Fixing what needs to be fixed:
                    #soup = BeautifulSoup(response.content, 'html.parser')
                    response = requests.get(url, headers=header).text
                    soup = BeautifulSoup(response)

                    # TITLE:
                    if article['title'] == None:
                        try:
                            article['title'] = ondalocalnicom_story(soup)['title']
                        except:
                            article['title'] == None
                    print('newsplease title', article['title'])
                    
                    # MAIN TEXT:
                    if article['maintext'] == None:
                        try:
                            article['maintext'] = ondalocalnicom_story(soup)['maintext']
                        except:
                            article['maintext'] == None
                    if  article['maintext']:
                        print('newsplease maintext', article['maintext'][:50])

                    # Fixing date:
                    article['date_publish'] = ondalocalnicom_story(soup)['date_publish']
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
                        print("DUPLICATE! Not inserted.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
                processed_url_count += 1
                print('\n',processed_url_count, '/', len(list_urls), 'articles have been processed ...\n')

            else:
                pass


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")