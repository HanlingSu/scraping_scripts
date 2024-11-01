#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Dec 22 2021

@author: diegoromero

This script updates bd-pratidin.com using sitemaps (only 1 month's worth of daily articles) 
and scraping urls from sections.

It can be run as often as one desires. 
 
"""
# Packages:
import random
import sys
from xxlimited import Xxo
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
db = MongoClient('mongodb://ml4pAdmin:ml4peace@research-devlab-mongodb-01.oit.duke.edu').ml4p


# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


## COLLECTING URLS
urls = []

## NEED TO DEFINE SOURCE!
source = 'bd-pratidin.com'


yearmap = "2022"
monthmap = 2
daystart = "1"
dayend = "28"


for i in range(int(daystart), int(dayend)+1):
    # Month
    if monthmap <10:
        monthstr = "0" + str(monthmap)
    else:
        monthstr = str(monthmap)

    # Day
    if i <10:
        daynum = "0" + str(i)
    else:
        daynum = str(i)

    # Correct url:
    #https://www.bd-pratidin.com/daily-sitemap/2022-01-06/sitemap.xml
    url = "https://www.bd-pratidin.com/daily-sitemap/" + yearmap + "-" + monthstr + "-" + daynum + "/sitemap.xml"

    print("Extracting from: ", url)
    reqs = requests.get(url, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    #print(soup)
    for link in soup.findAll('loc'):
        urls.append(link.text)

    print("Urls so far: ",len(urls))


## STEP 0: Define sections and max pages. 
sections = ['country','international-news','national','international','city-news','chayer-desh','economy','campus-online','coronavirus','minister-spake','chittagong-pratidin','probash-potro','city-roundup']
# CHANGE endnumbers for each section in accordance with how far 
# back you need to go:
#endnumber = ['7568','3178','2143','1','2432','309','9','628','1214','219','441','703','32']
#update:
endnumber = ['20','20','20','1','20','20','20','20','20','20','20','20','20']

for section in sections:
    indexword = sections.index(section)
    endnumberx = endnumber[indexword]

    for i in range(1, int(endnumberx)+1):
        if i == 1:
            url = "https://www.bd-pratidin.com/" + section  
        else:
            numpage = (i - 1)*14
            url = "https://www.bd-pratidin.com/" + section + "/" + str(numpage)
        
        print("Section: ", section, " -> URL: ", url)

        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        for link in soup.find_all('a'):
            urls.append(link.get('href')) 
        print("URLs so far: ", len(urls))

# STEP 1: Get rid or urls from blacklisted sources
blpatterns = ['/health/', '/horoscope/', '/mixter/', '/open-air-theater/', '/readers-column/', '/saturday-morning/', '/archive/', '/images/', '/news_images/', '/editorial/', '/entertainment-news/', '/Friday-various/', '/mohan-ekushey-special/', '/money-market-business/', '/sport-news/', 'Incapsula_Resource', '/islam/', '/features/', '/kolkata/','/t20-world-cup-2021/', '/campus-online/', '/agriculture-nature/', '/various-lifestyles/', '/various-city-roundup/', '/various/']
yearslist = list(range(2021,2023))

clean_urls = []
for url in urls:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            try: 
                if "bd-pratidin.com" in url:
                    clean_urls.append(newurl)
                else:
                    year_patterns = 0
                    for i in yearslist:
                        yeararticle = "/" + str(i) + "/"
                        if yeararticle in url:
                            year_patterns = year_patterns + 1
                    if year_patterns > 0:
                        count_patterns = 0
                        for pattern in blpatterns:
                            if pattern in url:
                                count_patterns = count_patterns + 1
                        if count_patterns == 0:
                            newurl = "https://www.bd-pratidin.com/" + url 
                            clean_urls.append(newurl)
            except:
                pass

# List of unique urls:
list_urls = list(set(clean_urls))

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
            if "bd-pratidin.com" in url:
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
                    article['source_domain'] = "bd-pratidin.com"
                    
                    ## Fixing what needs to be fixed:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # TITLE:
                    #if article['title'] == None:
                    try:
                        contains_title = soup.find("meta", {"property":"og:title"})
                        article_title = contains_title['content']
                        article['title'] = article_title
                    except:
                        article_title = article['title']
                        article['title'] = article_title
                    # MAIN TEXT:
                    #if article['maintext'] == None:
                    try:
                        maintext_contains = soup.findAll("p")
                        maintext = maintext_contains[0].text + " " + maintext_contains[1].text + " " + maintext_contains[2].text
                        article['maintext'] = maintext
                    except:
                        article_text = article['maintext']
                        article['maintext'] = article_text
                    # DATE
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
                        #print(article['date_publish'].month)
                        #print(article['title'])
                        #print("TEXT: ", article['maintext'])
                        print("Date extracted: ", article['date_publish'], " + Inserted! in ", colname, " - number of urls so far: ", url_count)
                        db['urls'].insert_one({'url': article['url']})
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