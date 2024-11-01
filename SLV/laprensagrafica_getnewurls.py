#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Nov 29 2021
Modified on May 10, 2023

@author: diegoromero

This script updates laprensagrafica.com using historical sitemaps.
It can be run whenever necessary. 
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
import urllib
import urllib.request
from urllib.request import urlopen
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
#db = MongoClient('mongodb://ml4pAdmin:ml4peace@research-devlab-mongodb-01.oit.duke.edu').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


## COLLECTING URLS
urls = []
siteurls = []

## NEED TO DEFINE SOURCE!
source = 'laprensagrafica.com'

###############################
# Custom Parser
def laprensagraficacom_story(soup):
    """
    Function to pull the information we want from laprensagrafica.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    
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
        maintext_contains = soup.find("div", {"class":"news-body"}).text
        #maintext = maintext_contains[2].text + " " + maintext_contains[3].text
        hold_dict['maintext'] = maintext_contains
        #
        #maintext_contains = soup.findAll("p")
        #maintext = maintext_contains[2].text + " " + maintext_contains[3].text
        #hold_dict['maintext'] = maintext
    except: 
        try:
            maintext_contains = soup.find("div", {"class":"nota"}).text
            hold_dict['maintext'] = maintext_contains
        except:
            hold_dict['maintext']  = None

    # Get Date
    try:
        contains_date = soup.findAll("time")[0]
        contains_date = contains_date["datetime"]
        contains_date = contains_date.replace("T"," ")
        contains_date = contains_date.replace("-"," ")
        vectordate = contains_date.split()
        # day, month, year:
        daystr = vectordate[2]
        monthstr = vectordate[1]
        yearstr = vectordate[0]
        article_date = datetime(int(yearstr),int(monthstr),int(daystr))
        hold_dict['date_publish'] = article_date
    except:
        try:
            contains_date = soup.find("time", {"class":"news-date"})
            contains_date = contains_date['datetime']
            article_date = dateparser.parse(contains_date,date_formats=['%d/%m/%Y'])
            hold_dict['date_publish'] = article_date  
        except:
            try:
                contains_date = soup.find("meta", {"name":"cXenseParse:recs:publishtime"})
                contains_date = contains_date['content']
                article_date = dateparser.parse(contains_date,date_formats=['%d/%m/%Y'])
                hold_dict['date_publish'] = article_date  
            except:
                hold_dict['date_publish'] = None
   
    return hold_dict 
###############################

# STEP 0 -> UPDATE GETTING URLS FROM THE LATEST SITEMAP 
#class AppURLopener(urllib.request.FancyURLopener):
#    version = "Mozilla/5.0"
#opener = AppURLopener()

pagenumbers = ["18"]

for page in pagenumbers:
    for i in range(3,4):
        sitemapurl = "https://www.laprensagrafica.com/_static/sitemaps/lpg-" + page + "-" + str(i) + ".txt"
        print("Extracting from: ", sitemapurl)

        #file = opener.open(sitemapurl)
        #file = urllib.request.urlopen(sitemapurl)
        #file = urlopen(sitemapurl)

        req = requests.get(sitemapurl, headers = headers)
        #file = BeautifulSoup(req.content, 'html.parser')
        file = BeautifulSoup(req.text, 'html.parser')
        soup_string = str(file)
        vectorurls = soup_string.split()
        #print(soup_string, len(soup_string))
        for link in vectorurls:
            # print(link)
            urls.append(link) 

        #for line in file:
        #    decoded_line = line.decode("utf-8")
        #    urls.append(decoded_line)
        print("URLs so far: ", len(urls))

        #sitemapurl = "https://www.laprensagrafica.com/sitemaps/news-daily.xml" # CHANGE if necessary
        #print("Extracting from: ", sitemapurl)
        #reqs = requests.get(sitemapurl, headers=headers)
        #soup = BeautifulSoup(reqs.text, 'html.parser')
        #for link in soup.findAll('loc'):
        #    urls.append(link.text)

        # Manually check urls:
        #list_urls = list(set(urls))
        #dftest = pd.DataFrame(list_urls)  
        #dftest.to_csv('/Users/diegoromero/Downloads/test.csv')  
        #print("DONE")

        # STEP 2: Get rid or urls from blacklisted sources
        blpatterns = ['/deportes/', '/opinion/', '/ella/', '/farandula/', '/salud/', '/tendencias/', '/blogs.', '/tag/', '/img/', '/7s.', '/Meme-', '/mujer/', '/revistas/','/seccion/']
        clean_urls = []
        for url in urls:
            if "laprensagrafica.com" in url:
                count_patterns = 0
                for pattern in blpatterns:
                    if pattern in url:
                        count_patterns = count_patterns + 1
                if count_patterns == 0:
                    clean_urls.append(url)
        # List of unique urls:
        list_urls = list(set(clean_urls))

        print("Total number of USABLE urls found: ", len(list_urls))


        ## INSERTING IN THE DB:
        url_count = 0
        for url in list_urls[::-1]:
            if url == "":
                pass
            else:
                if url == None:
                    pass
                else:
                    if "laprensagrafica.com" in url:
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
                            soup = BeautifulSoup(response.content, 'html.parser')

                            # Title:
                            article['title'] = laprensagraficacom_story(soup)['title']

                            # Main Text
                            if article['maintext'] == None:
                                article['maintext'] = laprensagraficacom_story(soup)['maintext']

                            # Date of Publication
                            article['date_publish'] = laprensagraficacom_story(soup)['date_publish']

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
                                print(" ++ DATE: ", article['date_publish'], " and month: ",article['date_publish'].month)
                                print(" ++ TITLE: ", article['title'][0:20], " ++ MAIN TEXT: ", article['maintext'][0:30])
                                pogressm = url_count/len(list_urls)
                                print("Inserted! in ", colname, " - Progress: ", pogressm)
                            except DuplicateKeyError:
                                url_count = url_count + 1
                                pogressm = url_count/len(list_urls)
                                print("DUPLICATE! Not inserted. Progress: ", pogressm)
                        except Exception as err: 
                            print("ERRORRRR......", err)
                            pass
                    else:
                        pass


        print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")