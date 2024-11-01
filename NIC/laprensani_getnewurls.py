#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Nov 11 2021

@author: diegoromero

This script updates 'laprensani.com' using daily sitemaps.
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
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from dotenv import load_dotenv
from bs4 import BeautifulSoup
# %pip install dateparser
import dateparser
import pandas as pd

import time

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}



# Custom Parser:
def laprensanicom_story(soup):
    """
    Function to pull the information we want from laprensani.com stories
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
        maintext = soup.find('p', attrs={'class':'entry-excerpt entry-excerpt-content-custom'}).text
        #soup.find("strong").text <p class="entry-excerpt entry-excerpt-content-custom">
        hold_dict['maintext'] = maintext

    except: 
        hold_dict['maintext']  = None
    
    # Get Date
    try:
        contains_date = soup.find("meta", {"property": "article:published_time"})
        article_date = dateparser.parse(contains_date['content'])
        hold_dict['date_publish'] = article_date  

    except:
        hold_dict['date_publish'] = None  

    return hold_dict 


## NEED TO DEFINE SOURCE!
source = 'laprensani.com'

## STEP 0: Define dates
years = [2022]

months = range(8, 12)


for year in years:
    yearstr = str(year)
    for month in months:
        ## List of URLS:
        urls = []
        # Month
        if month <10:
            monthstr = "0" + str(month)
        else:
            monthstr = str(month)

        #URL from archive: 
        for i in range(1,5):
            if i == 1:
                url = "https://www.laprensani.com/" + yearstr + "/" + monthstr
            else:
                url = "https://www.laprensani.com/" + yearstr + "/" + monthstr + "/page/" + str(i)

            print("Extracting from: ", url)
            time.sleep(2)
            reqs = requests.get(url, headers=headers)
            soup = BeautifulSoup(reqs.text, 'html.parser')

            messagef = soup.find("h1", {"class":"page-title"}).text
            if "¡Vaya! No se puede encontrar" in messagef:
                print("No more pages this month")
                break


            #print(soup)
            #for link in soup.findAll('loc'):
            #    urls.append(link.text)

            for link in soup.find_all('a'):
                urls.append(link.get('href')) 
            print("URLs so far: ", len(urls))

        print("Total RAW number of urls found for ", yearstr, "/", monthstr, "/", " is: ", len(urls))
        # STEP 1: Get rid of urls from blacklisted sources
        blpatterns = ['/aqui-entre-nos/', '/vida/', '/empresariales/', '/editorial/', '/opinion/', '/deportes/']

        # List of unique urls:
        dedup = list(set(urls))

        list_urls = []
        for url in dedup:
            if url == "":
                pass
            else:
                if url == None:
                    pass
                else:
                    try: 
                        if 'laprensani.com' in url:
                            count_patterns = 0
                            for pattern in blpatterns:
                                if pattern in url:
                                    count_patterns = count_patterns + 1
                            if count_patterns == 0:
                                list_urls.append(url)
                    except:
                        pass

        # Manually check urls:
        #list_urls = list(set(urls))
        #dftest = pd.DataFrame(list_urls)  
        #dftest.to_csv('/Users/diegoromero/Downloads/test.csv')  

        print("Total number of USABLE urls found for ", yearstr, "/", monthstr, "/", " is: ", len(list_urls))


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
                    if 'laprensani.com' in url:
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
                            article['source_domain'] = 'laprensani.com'

                            ## Fixing what needs to be fixed:
                            soup = BeautifulSoup(response.content, 'html.parser')

                            # TITLE:
                            if article['title'] == None:
                                try:
                                    article['title'] = laprensanicom_story(soup)['title']
                                except:
                                    article['title'] == None
                            print('newsplease title', article['title'])
       
                            # MAIN TEXT:
                            if article['maintext'] == None:
                                try:
                                    article['maintext'] = laprensanicom_story(soup)['maintext']
                                except:
                                    article['maintext'] == None
                            if article['maintext']:
                                print('newsplease maintext', article['maintext'][:50])

                            # Fixing date:
                            article['date_publish'] = laprensanicom_story(soup)['date_publish']
                            
                            if article['date_publish'] == None:
                                article['date_publish'] = datetime(year,month,1)
                            
                            print('newsplease date', article['date_publish'])


                            ## Inserting into the db
                            try:
                                #year = article['date_publish'].year
                                #month = article['date_publish'].month
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
                                # print("Duplicated, but fixing:")
                                # # Delete previous record:
                                # myquery = { "url": url}
                                # db[colname].delete_one(myquery)
                                # # Adding new record:
                                # db[colname].insert_one(article)
                                # url_count = url_count + 1
                                # #print("TEXT: ",article['maintext'][0:30]," + Title: ",article['title'][0:10])
                                # print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                                # db['urls'].insert_one({'url': article['url']})
                        except Exception as err: 
                            print("ERRORRRR......", err)
                            pass
                        processed_url_count += 1
                        print('\n',processed_url_count, '/', len(list_urls), 'articles have been processed ...\n')

                    else:
                        pass


        print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")