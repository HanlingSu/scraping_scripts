#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Nov 11 2021

@author: diegoromero

This script updates astroawani.com using monthly sitemaps.
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

import time

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
#db = MongoClient('mongodb://ml4pAdmin:ml4peace@research-devlab-mongodb-01.oit.duke.edu').ml4p

# headers for scraping
#headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}

#headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Safari/605.1.15 Version/13.0.4'}
#headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

#headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}

headers = {'User-Agent': 'MachineLearningForPeaceBot/1.0 (+https://mlp.trinity.duke.edu/#en)'}

## NEED TO DEFINE SOURCE!
source = 'astroawani.com'

## STEP 0: Define Year(s) and Month(s)
years = ["2021"]
#years = ["2013","2014","2015","2016","2017","2018","2019","2020","2021","2022"]
month_str = 10
month_end = 12



repeat_urls = []
for year in years:
    for i in range(int(month_str), int(month_end)+1):
        ## COLLECTING URLS (per day)
        urls = []
        # Month
        if i <10:
            monthstr = "0" + str(i)
        else:
            monthstr = str(i)

        # Sitemap URL:
        #https://www.astroawani.com/sitemap/article-2013-08.xml
        url = "https://www.astroawani.com/sitemap/article-" + str(year) + "-" + monthstr + ".xml"

        print("Extracting from: ", url)
        time.sleep(1)
        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')
        #print(soup)
        for link in soup.findAll('loc'):
            urls.append(link.text)
        #for link in soup.find_all('a'):
        #    urls.append(link.get('href')) 

        # Print Progress:
        print("URLs for ", year, "-", monthstr, ":", len(urls))


        # STEP 1: Get rid or urls from blacklisted sources
        blpatterns = ['.jpg','/img.']

        clean_urls = []
        for url in urls:
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
                            #newurl = "https://www.astroawani.com" + url 
                            clean_urls.append(url)
                    except:
                        pass

        # List of unique urls:
        list_urls = list(set(clean_urls))

        # Manually check urls:
        #list_urls = list(set(urls))
        #dftest = pd.DataFrame(list_urls)  
        #dftest.to_csv('/Users/diegoromero/Downloads/test.csv')  

        print("Total number of USABLE urls found for ", year, "-", monthstr, ":", len(list_urls))


        ## INSERTING IN THE DB:
        url_count = 0
        for url in list_urls:
            if url == "":
                pass
            else:
                if url == None:
                    pass
                else:
                    if "astroawani.com" in url:
                        print(url, "FINE")
                        ## SCRAPING USING NEWSPLEASE:
                        try:
                            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
                            #header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                            header = {'User-Agent': 'MachineLearningForPeaceBot/1.0 (+https://mlp.trinity.duke.edu/#en)'}
                            response = requests.get(url, headers=header)
                            # process
                            article = NewsPlease.from_html(response.text, url=url).__dict__
                            # add on some extras
                            article['date_download']=datetime.now()
                            article['download_via'] = "Direct2"
                            article['language'] = 'ms'
                            
                            ## Fixing what needs to be fixed:
                            soup = BeautifulSoup(response.content, 'html.parser')
                            #print(soup)
                            #time.sleep(12)

                            # Fixing date:
                            if article['date_publish'] == None:
                                article['date_publish'] = datetime(int(year),int(monthstr),1)
                            else:
                                if article['date_publish'].month != int(monthstr):
                                    if article['date_publish'].year != int(year):
                                        article['date_publish'] = datetime(int(year),int(monthstr),1)

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
                                print("++ DATE: ",article['date_publish'])
                                #print(article['date_publish'].month)
                                print("++ TITLE: ",article['title'])
                                print("++ MAIN TEXT",article['maintext'])
                                print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                                db['urls'].insert_one({'url': article['url']})
                            except DuplicateKeyError:
                                print("DUPLICATE! Not inserted.")
                                #print("Duplicated, but fixing:")
                                # Delete previous record:
                                #myquery = { "url": url}
                                #db[colname].delete_one(myquery)
                                # Adding new record:
                                #db[colname].insert_one(article)
                                #url_count = url_count + 1
                                #print("TEXT: ",article['maintext'][0:30]," + Title: ",article['title'][0:10])
                                #print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                                #db['urls'].insert_one({'url': article['url']})
                        except Exception as err: 
                            print("ERRORRRR......", err)
                            pass
                    else:
                        pass


        print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")