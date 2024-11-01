#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Nov 11 2021

@author: mitali

This script updates livehindustan.com 
 
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
import math
import time


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## NEED TO DEFINE SOURCE!
source = 'livehindustan.com'


def livehindustan_story(soup):

    """
    Function to pull the information we want from livehindustan.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}

    # Get Title: 
    try:
        article_title = soup.find("h1",{"class":"page-hdng"}).text
        hold_dict['title']  = article_title   
    except:
        hold_dict['title']  = None
        
    # Get Main Text:
    try:
        maintext = soup.findAll("p",attrs={"class": None})
        if maintext[0].text != "शायद आप ऐड ब्लॉकर का इस्तेमाल कर रहे हैं। पढ़ना जारी रखने के लिए ऐड ब्लॉकर को बंद करके पेज रिफ्रेश करें।":
          text = maintext[0].text
        else:
          text = maintext[1].text
        text = text.strip()
        hold_dict['maintext'] = text
    except:
        hold_dict['maintext'] = None  

    # Get Date
    try:
        datebit = soup.find("span", {"class":"tm-stmp"}).text
        datevector = datebit.split(", ")[1].split(" ")
        datevector = " ".join(datevector[:3])
        article_date = datetime.strptime(datevector,'%d %b %Y')
        #article_date = article_date.strftime('%d-%m-%Y')
        hold_dict['date_publish'] = article_date
    except:
        hold_dict['date_publish'] = None
   
    return hold_dict 

# list_urls=[]

# urlsections = ["https://www.livehindustan.com/uttar-pradesh/news-","https://www.livehindustan.com/bihar/news-","https://www.livehindustan.com/ncr/news-",
# "https://www.livehindustan.com/uttarakhand/news-","https://www.livehindustan.com/jharkhand/news-","https://www.livehindustan.com/madhya-pradesh/news-",
# "https://www.livehindustan.com/rajasthan/news-","https://www.livehindustan.com/chhattisgarh/news-","https://www.livehindustan.com/haryana/news-",
# "https://www.livehindustan.com/himachal-pradesh/news-","https://www.livehindustan.com/maharashtra/news-","https://www.livehindustan.com/punjab/news-",
# "https://www.livehindustan.com/jammu-and-kashmir/news-","https://www.livehindustan.com/odisha/news-","https://www.livehindustan.com/west-bengal/news-",
# "https://www.livehindustan.com/chandigarh/news-","https://www.livehindustan.com/tripura/news-","https://www.livehindustan.com/gujarat/news-",
# "https://www.livehindustan.com/national/news-","https://www.livehindustan.com/international/news-","https://www.livehindustan.com/business/news-",
# "https://www.livehindustan.com/career/news-"]

# urls = []
# # empty searchers: -> 300 pages, only goes back to Dec 2022. 
# for baseurl in urlsections:

#     subsections = []
#     s = "/" + baseurl.split("/")[-2] +"/"

#     print(s)
#     # Step 1: obtain urls in each page
#     for j in range(1,300):

#         url = baseurl + str(j)
#         print(url)

#         req = requests.get(url, headers = headers)
#         soup = BeautifulSoup(req.content, 'html.parser')
        
#         for link in soup.find_all('a'):
#             link = link.get('href')
#             if link == "" or link == None:
#                 pass
#             elif re.search('^'+s+'.*'+'/news$',link):
#                 if link not in subsections:
#                     subsections.append(link)
#             elif re.search('^'+s+'.*'+'/$',link):
#                 pass
#             else:
#                 urls.append(link) 

#     if len(subsections) !=0:
#         for j in range(1,300):
#             for suburl in subsections:
#                 url = "https://www.livehindustan.com" + suburl + '-' +str(j)
#                 print(url)

#                 req = requests.get(url, headers = headers)
#                 soup = BeautifulSoup(req.content, 'html.parser')
                
#                 for link in soup.find_all('a'):
#                     link = link.get('href')
#                     urls.append(link) 

    
#     #print(subsections)
#     #print(len(subsections))
    
#     # Step 2: Get rid or urls from blacklisted sources and fix urls
#     blpatterns = ['/cricket/','/photos/','/videos/','/entertainment/','/astrology/','/lifestyle/','/gadgets/',
#     '/auto/', '/shop-now', '/articles-for-you/', '/viral-news/', '/sports/', '/jokes/','twitter']

#     clean_urls = []
#     for url in urls:
        
#         if url == "":
#             pass
#         else:
#             if url == None:
#                 pass
#             else:
#                 count_patterns = 0
#                 for pattern in blpatterns:
#                     if pattern in url:
#                         count_patterns = count_patterns + 1     
#                 if count_patterns == 0:
#                     #print(url)
#                     if not "https://www.livehindustan.com" in url:
#                         url = "https://www.livehindustan.com" + url
#                     clean_urls.append(url)
        
#     list_urls = list(set(clean_urls))
#     print(list_urls)
#     print("Total number of USABLE urls found: ", len(list_urls))
    
    
#     ## INSERTING IN THE DB:
#     url_count = 0
#     for url in list_urls:
#         print(url)
#         ## SCRAPING USING NEWSPLEASE:
#         try:
#             #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
#             header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
#             response = requests.get(url, headers=header)
#             # process
#             article = NewsPlease.from_html(response.text, url=url).__dict__
#             # add on some extras
#             article['date_download'] = datetime.now()
#             article['download_via'] = "LocalIND"
#             article['source_domain'] = source 
            
            
#             ## Fixing Date + Title + Main Text
#             soup = BeautifulSoup(response.content, 'html.parser')
#             extracted_data  =  livehindustan_story(soup)
#             article['date_publish'] =  extracted_data['date_publish']
#             article['title'] =  extracted_data['title']
#             article['maintext'] =  extracted_data['maintext']

           
#             ## Inserting into the db
#             try:
#                 year = article['date_publish'].year
#                 month = article['date_publish'].month
#                 colname = f'articles-{year}-{month}'
#             except:
#                 colname = 'articles-nodate'
#             try:
#                 url_count = url_count + 1
#                 # Inserting article into the db:
#                 db[colname].insert_one(article)
#                 print(" + Date: ", article['date_publish'], " + Main Text: ", article['maintext'][0:50], " + Title: ", article['title'][0:25])
#                 print("Inserted! in ", colname, " - number of urls so far: ", url_count)
#                 db['urls'].insert_one({'url': article['url']})
#             except DuplicateKeyError:
#                 print("DUPLICATE! Not inserted.")
#         except Exception as err: 
#             print("ERRORRRR......", err)
#             pass

#     print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
    
# STEP 0: Get sitemap urls:
siteurls = []

years = ['2023', '2024']
months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
days = range(1, 14)
for year in years:
  for month in months:
    for day in days:
      sitmp = 'https://www.livehindustan.com/lhfeed/sitemap/' + year + '/' + month + '-' + str(day) + '.xml'
      #print(sitmp)
      siteurls.append(sitmp)

print(siteurls)

print("Number of sitemaps found: ", len(siteurls))


# STEP 1: Get urls of articles from sitemaps:
for sitmp in siteurls:
    urls = []
    print("Extracting from: ", sitmp)
    reqs = requests.get(sitmp, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    time.sleep(10)
    
    for link in soup.findAll('loc'):
          # Step 2: Get rid or urls from blacklisted sources and fix urls
      blpatterns = ['/entertainment/','/career/','/business/','/entertainment/','/astrology/','/lifestyle/','/gadgets/','/auto/', '/web-stories/', '/photos/', '/videos/', 'https://epaper.livehindustan.com/', '/jokes/','twitter']
      clean_urls = []
      if link == "":
          pass
      else:
          if link == None:
              pass
          else:
              count_patterns = 0
              for pattern in blpatterns:
                  if pattern in link:
                      count_patterns = count_patterns + 1     
              if count_patterns == 0:
                  #print(url)
                  if "livehindustan.com/" in link:
                    urls.append(link.text)


    # List of unique urls:
    list_urls = list(set(urls))

    print("Total number of USABLE urls found: ", len(list_urls))
    #time.sleep(30)

    ## INSERTING IN THE DB:
    url_count = 0
    for url in list_urls:
        if url == "":
            pass
        else:
            if url == None:
                pass
            else:
                if "livehindustan.com" in url:
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
    time.sleep(3)

