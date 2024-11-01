#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Jan 7 2023

@author: diegoromero

This script updates kaztag.kz using sitemaps. 
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
uri = 'mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true'
db = MongoClient(uri).ml4p
#db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
#db = MongoClient('mongodb://ml4pAdmin:ml4peace@research-devlab-mongodb-01.oit.duke.edu').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

###########################################################
def kaztagkz_story(soup):
    """
    Function to pull the information we want from kaztag.kz stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}

    # Get Title: 
    try:
        article_title = soup.find("title").text
        hold_dict['title'] = article_title   
    except:
        try:
            contains_title = soup.find("meta",{"property":"og:title"})
            article_title = contains_title["content"]
            hold_dict['title'] = article_title 
        except:
            hold_dict['title'] = None
        
    # Get Main Text:
    try:
        text = soup.find("div",{"class":"post-content"}).text
        datevector = text.split()
        datevectorc = datevector[7:]
        maintext = ' '.join(str(x) for x in datevectorc)
        hold_dict['maintext'] = maintext
    except:
        try:
            sentences = soup.findAll("p")
            #print(len(sentences))
            text = ""
            count = 0
            for sent in sentences:
              count = count + 1
              if count >= 1:
                  text = text + " " + sent.text
              else:
                pass
            text = text.lstrip()
            hold_dict['maintext'] = text
        except:
            hold_dict['maintext'] = None  

    # Get date:
    try:
        months_list = ["Қаңтар","Ақпан","Наурыз","Сәуiр","Мамыр","Маусым","Шiлде","Тамыз","Қыркүйек","Қазан","Қараша","Желтоқсан"]
        containsdate = soup.find("div",{"class":"post-byline"}).text
        dtext = containsdate.replace("\n", "")
        dtext = dtext.replace(",", "")
        datevector = dtext.split()
        dayx = datevector[0]
        monthx = datevector[1]
        if monthx in months_list:
          monthxn = months_list.index(monthx) + 1
        yearx = datevector[2]
        article_date = datetime(int(yearx),int(monthxn),int(dayx))
        hold_dict['date_publish'] = article_date
    except:
        try:
            allstuff = soup.findAll("div",{"class":"t-info"})
            datestuff = allstuff[0].text
            urlindex = datestuff.index("-")
            daynum = datestuff[urlindex-2:urlindex]
            monthnum = datestuff[urlindex+1:urlindex+3]
            yearnum = datestuff[urlindex+4:urlindex+8]
            article_date = datetime(int(yearnum),int(monthnum),int(daynum))
            hold_dict['date_publish'] = article_date
        except:
            hold_dict['date_publish'] = None
   
    return hold_dict
###########################################################

## COLLECTING URLS
siteurls = []

## NEED TO DEFINE SOURCE!
source = 'kaztag.kz'

# STEP 0: Get sitemap urls:
#url = "https://kaztag.kz/sitemap.xml"
#print("Extracting from: ", url)
#reqs = requests.get(url, headers=headers)
#soup = BeautifulSoup(reqs.text, 'html.parser')
#for link in soup.findAll('loc'):
#    siteurls.append(link.text)

#for link in soup.find_all('a'):
#    urls.append(link.get('href')) 

#dftest = pd.DataFrame(siteurls)  
#dftest.to_csv('/Users/diegoromero/Downloads/test.csv')  

#print("Number of sitemaps found today: ", len(siteurls))


# STEP 1: Get urls of articles from sitemaps:
#for sitmp in siteurls:
#    urls = []
#    print("Extracting from: ", sitmp)
#    reqs = requests.get(sitmp, headers=headers)
#    soup = BeautifulSoup(reqs.text, 'html.parser')
#    for link in soup.findAll('loc'):
#        urls.append(link.text)
    #for link in soup.find_all('a'):
    #    urls.append(link.get('href')) 
#    print("URLs so far: ", len(urls))

for page in range(1,330):
    urls = []
    urlp = "https://kaztag.kz/kz/news/?PAGEN_1=" + str(page)

    print("Extracting from: ", urlp)
    reqs = requests.get(urlp, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    #for link in soup.findAll('loc'):
    #    urls.append(link.text)
    for link in soup.find_all('a'):
        urls.append(link.get('href')) 
    print("URLs so far: ", len(urls))

    # STEP 2: Get rid or urls from blacklisted sources
    blpatterns = ['/sport/','/tags/','?PAGEN_1']

    clean_urls = []
    for url in urls:
        count_patterns = 0
        for pattern in blpatterns:
            if pattern in url:
                count_patterns = count_patterns + 1
        if count_patterns == 0:
            if "kaztag.kz" in url:
                clean_urls.append(url)  
            else:
                newurl = "https://kaztag.kz" + url 
                clean_urls.append(newurl)
        else:
            pass
            
    # List of unique urls:
    list_urls = list(set(clean_urls))

    ## INSERTING IN THE DB:
    if len(list_urls) == 0:
        print("Total number of USABLE urls found: ", len(list_urls), "No urls.")
    else:
        print("Total number of USABLE urls found: ", len(list_urls), "Begining scraping process.")

        url_count = 0
        for url in list_urls:
            if url == "":
                pass
            else:
                if url == None:
                    pass
                else:
                    if "kaztag.kz" in url:
                        print(" + URL:",url)
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

                            if "/kz/" in url:
                                article['language'] = 'kk'
                            else:
                                if "/en/" in url:
                                    article['language'] = 'en'
                                else:
                                    if "/ru/" in url:
                                        article['language'] = 'ru'
                                    
                            ## Fixing main texts when needed:
                            soup = BeautifulSoup(response.content, 'html.parser')

                            # Get Main Text:
                            article['maintext'] = kaztagkz_story(soup)['maintext']

                            # Get Title
                            article['title'] = kaztagkz_story(soup)['title']

                            #Date:
                            article['date_publish'] = kaztagkz_story(soup)['date_publish']

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
                                print(article['date_publish'])
                                print("article Title: ", article['title'][0:50])
                                print("article Text: ", article['maintext'][0:100])
                                print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                                #db['urls'].insert_one({'url': article['url']})
                            except DuplicateKeyError:
                                print("DUPLICATE! FIXING.")
                                myquery = { "url": url}
                                db[colname].delete_one(myquery)
                                # Inserting article into the db:
                                db[colname].insert_one(article)
                                # count:
                                url_count = url_count + 1
                                print(article['date_publish'])
                                print("article Title: ", article['title'][0:50])
                                print("article Text: ", article['maintext'][0:100])
                                print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        except Exception as err: 
                            print("ERRORRRR......", err)
                            pass
                    else:
                        pass

        print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db, from page", str(page))