#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Updated on March 3 2024

@author: Togbedji 

This script for vijayavani.net
 
"""
# Packages:
#import time
#import random
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
import math
import requests



# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## NEED TO DEFINE SOURCE!
source = 'vijayavani.net'

#################
# Custom Parser #
# Custom Parser
def vijayavani_story(soup):
    """
    Function to pull the information we want from indiatimes.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}

    # Get Title:
    try:
        #article_title = soup.find("title").text
        article_title = soup.find("h1", {"class":"tdb-title-text"}).text
        hold_dict['title']  = article_title.replace('\u200b', '')

    except:
        article_title = None
        hold_dict['title']  = None

    # Get Main Text:
    try:
        maintext_contains = soup.find("div", {"class":"td_block_wrap tdb_single_content tdi_59 td-pb-border-top td_block_template_5 td-post-content tagdiv-type"}).text
        hold_dict['maintext'] = maintext_contains.replace('\u200b', '')
    except:
        maintext = None
        hold_dict['maintext']  = None


    # Get Date:
    try:
        date_contains = soup.find("time", {"class":"entry-date updated td-module-date"}).text
        date = dateparser.parse(date_contains, date_formats=['%d/%m/%Y'])
        hold_dict['date_publish'] = date
    except:
        hold_dict['date_publish'] = None

    return hold_dict
##
#################


# sections = ['%e0%b2%b8%e0%b2%ae%e0%b2%b8%e0%b3%8d%e0%b2%a4-%e0%b2%95%e0%b2%b0%e0%b3%8d%e0%b2%a8%e0%b2%be%e0%b2%9f%e0%b2%95', '%e0%b2%a6%e0%b3%87%e0%b2%b6','%e0%b2%b5%e0%b2%bf%e0%b2%a6%e0%b3%87%e0%b2%b6', '%e0%b2%aa%e0%b3%8d%e0%b2%b0%e0%b2%a6%e0%b3%87%e0%b2%b6-%e0%b2%b8%e0%b2%ae%e0%b2%be%e0%b2%9a%e0%b2%be%e0%b2%b0', 'loka-samara-2024', 'jai-shri-rama', 'face-2-face', 'column']
# positions = [4553, 4083, 875, 20196, 32, 18, 7, 394]


# for i in range(len(sections)):
#   section_name = sections[i]
#   page_num = positions[i]
  
#   #print(section_page)
#   for page in range(1, page_num +1):
#     if page ==1:
#         section_page = 'https://www.vijayavani.net/category/' + section_name
#     else:
#         section_page = 'https://www.vijayavani.net/category/' + section_name + "/page/" + str(page)
#     print(section_page)

#     reqs = requests.get(section_page, headers=headers)
#     soup = BeautifulSoup(reqs.text, 'html.parser')
#     #print(soup.find('div', {'id':'tdi_54'}))
    
#     urls = []
#     for link in soup.find('div', {'id':'tdi_60'}).find_all('a'):
#         #print(link)
#         urls.append(link.get('href')) 
#         urls = list(set(urls))
#         print("URLs so far: ",len(urls))

#     ## INSERTING IN THE DB:
#     url_count = 0
#     for url in urls:
#         if url == "":
#             pass
#         else:
#             if url == None:
#                 pass
#             else:
#                 if "vijayavani.net" in url:
#                     print(url, "FINE")
#                     ## SCRAPING USING NEWSPLEASE:
#                     try:
#                         #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
#                         header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
#                         response = requests.get(url, headers=header)
#                         soup = BeautifulSoup(response.text, 'html.parser')

#                         # process
#                         article = NewsPlease.from_html(response.text, url=url).__dict__
#                         # add on some extras
#                         article['date_download']=datetime.now()
#                         article['download_via'] = "Direct2"
#                         article['date_publish'] = vijayavani_story(soup)['date_publish']
#                         article['maintext'] = vijayavani_story(soup)['maintext']
                        
#                         ## Inserting into the db
#                         try:
#                             year = article['date_publish'].year
#                             month = article['date_publish'].month
#                             colname = f'articles-{year}-{month}'
#                             #print(article)
#                         except:
#                             colname = 'articles-nodate'
#                         try:
#                             #TEMP: deleting the stuff i included with the wrong domain:
#                             #myquery = { "url": final_url, "source_domain" : 'web.archive.org'}
#                             #db[colname].delete_one(myquery)
#                             # Inserting article into the db:
#                             #db[colname].insert_one(article)
#                             # count:
#                             url_count = url_count + 1
#                             print(article['date_publish'])
#                             #print(article['date_publish'].month)
#                             print(article['title'][0:100])
#                             print(article['maintext'][0:100])
#                             print("Inserted! in ", colname, " - number of urls so far: ", url_count)
#                             #db['urls'].insert_one({'url': article['url']})
#                         except DuplicateKeyError:
#                             print("DUPLICATE! Not inserted.")
#                     except Exception as err: 
#                         print("ERRORRRR......", err)
#                         pass
#                 else:
#                     pass


#     print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
#df_urls = pd.read_csv('C:/Users/Yoga/Downloads/urls/articles_urls.csv')
#def_urls = df_urls['urls']



siteurls = []
for i in range(1, 270):
  sitemap_link = 'https://www.vijayavani.net/post-sitemap' + str(i) + '.xml'
  siteurls.append(sitemap_link)

print(siteurls)

print("Number of sitemaps found: ", len(siteurls))



# STEP 1: Get urls of articles from sitemaps:
for sitmp in siteurls:
   urls = []
   print("Extracting from: ", sitmp)
   reqs = requests.get(sitmp, headers=headers)
   soup = BeautifulSoup(reqs.content, 'html.parser')
   
   for link in soup.findAll('loc'):
        urls.append(link.text)
        print(link)
    
   list_urls = list(set(urls))
   print("Total number of USABLE urls found: ", len(list_urls))
#     #time.sleep(30)

#def_urls = ['https://www.vijayavani.net/mumbai-register-7-wickets-win-against-rcb-in-wankhede','https://www.vijayavani.net/ex-ias-officer-gifts-ramcharitmanas-scripted-in-gold-to-ram-lalla-in-ayodhya','https://www.vijayavani.net/buddhism-is-a-separate-religion-hindus-should-get-permission-to-convert-what-is-the-gujarat-governments-clarification']
## INSERTING IN THE DB:
url_count = 0
for url in def_urls:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if "vijayavani.net" in url:
                ## SCRAPING USING NEWSPLEASE:
                try:
                    # count:
                    url_count = url_count + 1
                    #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
                    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                    response = requests.get(url, headers=header)
                    # process
                    article = NewsPlease.from_html(response.text, url=url).__dict__
                    # add on some extras
                    article['date_download']=datetime.now()
                    article['download_via'] = "Direct2"
                    article['source_domain'] = source


                    ## Fixing main texts when needed:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Title:
                    article['title'] = vijayavani_story(soup)['title']

                    # Main Text
                    article['maintext'] = vijayavani_story(soup)['maintext']

                    # Date of Publication
                    article['date_publish'] = vijayavani_story(soup)['date_publish']

                    # Get Main Text:
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
                        #db[colname].insert_one(article)
                        print("+ URL: ",url)
                        print("+ DATE: ",article['date_publish'].month)
                        print("+ TITLE: ",article['title'][0:200])
                        print("+ MAIN TEXT: ",article['maintext'][0:200])
                        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        pogressm = url_count/len(list_urls)
                        print(" --> Progress:", str(pogressm), " -- Sitemamp: ", sitmp)
                        #db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        pogressm = url_count/len(list_urls)
                        print("DUPLICATE! Not inserted. --> Progress:", str(pogressm), " -- Sitemamp: ", sitmp)
                except Exception as err:
                    print("ERRORRRR......", err)
                    #pass
            else:
                pass


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db. Now waiting 63 seconds...")
#time.sleep(3)
