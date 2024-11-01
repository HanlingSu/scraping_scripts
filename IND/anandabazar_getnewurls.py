#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Jun 9 2023

@author: diegoromero
         Togbedji Gansey

This script updates anandabazar.com using daily sitemaps
It can be run as often as one desires. 

Sitemaps:
#https://www.anandabazar.com/news-sitemap.xml (not comprehensive)

Better to scrape from sections:
#https://www.anandabazar.com/west-bengal/page-1
#https://www.anandabazar.com/west-bengal/page-500

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

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## NEED TO DEFINE SOURCE!
source = 'anandabazar.com'

########################################
##            Custom parser           ##   
########################################
def anandabazarcom_story(soup):
    """
    Function to pull the information we want from anandabazar.com stories
    """
    hold_dict = {}

    # Get Title: 
    try:
        article_titlec = soup.find("meta", {"property":"og:title"})
        article_title = article_titlec["content"]
        hold_dict['title']  = article_title
    except:
        hold_dict['title']  = article_title = None

    # Get Main Text:   
    try:
        listoftexts = soup.findAll("p")
        text = listoftexts[1].text
        text = text.strip()
        hold_dict['maintext'] = text
    except:
        hold_dict['maintext'] = None  

    # Get Date
    try:
        itms = soup.findAll("script", {"type":"application/ld+json"})
        for i in itms:
            if "datePublished" in str(i):
                texto = str(i)
                vectordate = texto.split()
                indexcount = 0
                for vec in vectordate:
                    indexcount = indexcount + 1
                    if "datePublished" in vec:
                        datebit = vectordate[indexcount]
                        datebit = datebit.replace("T"," ")
                        datebit = datebit.replace("-"," ")
                        datebit = datebit.replace('"','')
                        vecdatebit = datebit.split()
                        # day, month, year:
                        daystr = vecdatebit[2]
                        monthstr = vecdatebit[1]
                        yearstr = vecdatebit[0]
                        article_date = datetime(int(yearstr),int(monthstr),int(daystr))
                    else:
                        pass
            else:
                pass
        hold_dict['date_publish'] = article_date
    except:
        try: 
            itms = soup.findAll("script", {"type":"application/ld+json"})
            for i in itms:
                if "datePublished" in str(i):
                    texto = str(i)
                    vectordate = texto.split()
                    for vec in vectordate:
                        if "datePublished" in vec:
                            containsdate = vec
                            containsdate = containsdate.replace('":"',' ')
                            containsdate = containsdate.replace('","',' ')
                            containsdate = containsdate.replace(':',' ')
                            containsdate = containsdate.replace('"',' ')
                            veccontainsdate = containsdate.split()
                            for vct in veccontainsdate:
                                if "datePublished" in vct:
                                    indexp = veccontainsdate.index("datePublished")
                                    datebit = veccontainsdate[indexp+1]
                                    datebit = datebit.replace("T"," ")
                                    datebit = datebit.replace("-"," ")
                                    vecdatebit = datebit.split()
                                    # day, month, year:
                                    daystr = vecdatebit[2]
                                    monthstr = vecdatebit[1]
                                    yearstr = vecdatebit[0]
                                    article_date = datetime(int(yearstr),int(monthstr),int(daystr))
                                else:
                                    pass
                        else:
                            pass
                else:
                    pass
            hold_dict['date_publish'] = article_date
        except Exception as err:
            hold_dict['date_publish'] = None
    
    return hold_dict
########################################

# STEP 0: Extracting urls from key sections:
sections = ['/editorial/','/india/','/west-bengal/','/west-bengal/kolkata/','/west-bengal/north-bengal/','/west-bengal/bardhaman/','/west-bengal/midnapore/','/west-bengal/howrah-hooghly/','/west-bengal/purulia-birbhum-bankura/','/west-bengal/24-parganas/','/west-bengal/nadia-murshidabad/']
number = [80,500,500,200,200,150,70,80,80,80,90]

#sections = ['/india/','/west-bengal/']
#number = [2,2]


#https://www.anandabazar.com/west-bengal/page-1
#https://www.anandabazar.com/west-bengal/page-500
#https://www.anandabazar.com/west-bengal/kolkata/page-1
#https://www.anandabazar.com/west-bengal/north-bengal/page-500
#https://www.anandabazar.com/west-bengal/bardhaman/page-500
#     

for sect in sections:
    #time.sleep(2)
    ## COLLECTING URLS
    urls = []
    indexsect = sections.index(sect)
    numberx = number[indexsect]
    for i in range(1,numberx+1):
        url = "https://www.anandabazar.com" + sect + "page-" + str(i)

        print("Extracting from ", url)

        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        try:
            for link in soup.find('div', {'class':'df mt-16'}).find_all('a'):
                urlx = "https://www.anandabazar.com" + link.get('href')
                print(urlx)
                urls.append(urlx) 
        except:
            pass

        print("+ Number of urls so far: ", len(urls))

    # STEP 2: Get rid or urls from blacklisted sources
    dedup_urls = list(set(urls))
    blpatterns = ['/video/','/weddings/','/sports/','/entertainment/','/lifestyle/','/recipes/','viral','photogallery']
    list_urls = []
    for url in dedup_urls:
        if url == "":
            pass
        else:
            if url == None:
                pass
            else:
                count_patterns = 0
                for pattern in blpatterns:
                    if pattern in url:
                        count_patterns = count_patterns + 1
                if count_patterns == 0:
                    list_urls.append(url)

    print("Total number of USABLE urls found: ", len(list_urls), ".")

    ## INSERTING IN THE DB:
    url_count = 0
    for url in list_urls:
        if url == "":
            pass
        else:
            if url == None:
                pass
            else:
                if 'anandabazar.com' in url:
                    print("+ URL: ", url)
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
                        article['source_domain'] = 'anandabazar.com'
                        
                        ## Fixing Date, Title, and Text
                        soup = BeautifulSoup(response.content, 'html.parser')

                        # Title:
                        article['title'] = anandabazarcom_story(soup)['title']

                        # Text:
                        article['maintext'] = anandabazarcom_story(soup)['maintext']

                        # Date: 
                        article['date_publish'] = anandabazarcom_story(soup)['date_publish']
                        #print(article_date)

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
                            print("+ TITLE: ", article['title'][0:80])
                            print("+ TEXT: ", article['maintext'][0:100])
                            print("+ DATE: ", article['date_publish'])
                            print("+ Inserted: ", colname, " - number of urls so far: ", url_count, " from: ",sect)
                        except DuplicateKeyError:
                            print("DUPLICATE! Not inserted.")
                    except Exception as err: 
                        print("ERRORRRR......", err)
                        pass
                else:
                    pass

    print("Done inserting ", url_count, " manually collected urls from ", sect)