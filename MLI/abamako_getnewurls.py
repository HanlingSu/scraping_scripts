#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Aug 29, 2022

@author: diegoromero

This script updates news.abamako.com by creating urls (taking advantage of url patterns).
This script can be ran whenever needed, just make the necessary modifications.
 
"""
# Packages:
from pickletools import stringnl_noescape
import time
import random
import importlib
import sys
sys.path.append('../')
import os
import re
#from p_tqdm import p_umap
from tqdm import tqdm
from pymongo import MongoClient
import random
from urllib.parse import urlparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from pymongo.errors import CursorNotFound
import requests
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
source = 'news.abamako.com'

## Custom Scraper
## Custom Scraper
def newsabamakocom_story(soup):
  """
  Function to pull the information we want from news.abamako.com stories
  :param soup: BeautifulSoup object, ready to parse
  """
  hold_dict = {}

  # Get Title: 
  try:
      contains_title = soup.find("meta", {"property":"og:title"})
      article_title = contains_title['content']
      hold_dict['title']  = article_title   
  except:
      try:
          contains_title = soup.find("title")
          article_title = contains_title.text
          hold_dict['title']  = article_title  
      except:
          hold_dict['title']  = None
      
  # Get Main Text:
  try:
      contains_text = soup.findAll('span',{"class":"FullArticleTexte"})
      if len(contains_text) > 1:
          if len(contains_text) == 2:
              maintext = contains_text[0].text + contains_text[1].text
          else:
              maintext = contains_text[0].text + contains_text[1].text + contains_text[2].text
      else:
          maintext = contains_text[0].text
      hold_dict['maintext'] = maintext
  except: 
      try:
          contains_maintext = soup.find("meta", {"property":"og:description"})
          maintext = contains_maintext['content']
          hold_dict['maintext'] = maintext  
      except: 
          maintext = None
          hold_dict['maintext']  = None

  # Get Date
  try: 
      months = ['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre']
      months2 = ['janvier','fevrier','mars','avril','mai','juin','juillet','aout','septembre','octobre','novembre','decembre']
      try: 
          contains_date = soup.find("div", {"class":"FontArticleSource"}).text

          if "/201" in contains_date:
            contains_datelist = contains_date.split()
            for i in contains_datelist:
              if "/201" in i:
                indexdate = contains_datelist.index(i)
            datebit = contains_datelist[indexdate]
            datebit = datebit.replace("/", " ")
            datevector = datebit.split()
            dayx = datevector[0]
            monthx = datevector[1]
            yearx = datevector[2]
            article_date = datetime(int(yearx),int(monthx),int(dayx))
            hold_dict['date_publish'] = article_date
          else:
            if "/202" in contains_date:
              contains_datelist = contains_date.split()
              for i in contains_datelist:
                if "/202" in i:
                  indexdate = contains_datelist.index(i)
              datebit = contains_datelist[indexdate]
              datebit = datebit.replace("/", " ")
              datevector = datebit.split()
              dayx = datevector[0]
              monthx = datevector[1]
              yearx = datevector[2]
              article_date = datetime(int(yearx),int(monthx),int(dayx))
              hold_dict['date_publish'] = article_date
            else:
              contains_datelist = contains_date.split()
              for i in contains_datelist:
                if "201" in i:
                  indexdate = contains_datelist.index(i)
                else:
                  if "202" in i:
                    indexdate = contains_datelist.index(i)
              yearx = contains_datelist[indexdate] 
              dayx = contains_datelist[indexdate-2] 
              montht = contains_datelist[indexdate-1] 
              montht = montht.lower()
              if montht in months:
                monthx = months.index(montht) + 1
              else:
                monthx = months2.index(montht) + 1
              article_date = datetime(int(yearx),int(monthx),int(dayx))
              hold_dict['date_publish'] = article_date
      except:
          contains_date_list = soup.findAll("div", {"class":"FontArticleSource"})
          contains_date = contains_date_list[1].text
          if "/201" in contains_date:
            contains_datelist = contains_date.split()
            for i in contains_datelist:
              if "/201" in i:
                indexdate = contains_datelist.index(i)

            datebit = contains_datelist[indexdate]
            datebit = datebit.replace("/", " ")
            datevector = datebit.split()
            dayx = datevector[0]
            monthx = datevector[1]
            yearx = datevector[2]
            article_date = datetime(int(yearx),int(monthx),int(dayx))
            hold_dict['date_publish'] = article_date
          else:
            if "/202" in contains_date:
              contains_datelist = contains_date.split()
              for i in contains_datelist:
                if "/202" in i:
                  indexdate = contains_datelist.index(i)

              datebit = contains_datelist[indexdate]
              datebit = datebit.replace("/", " ")
              datevector = datebit.split()
              dayx = datevector[0]
              monthx = datevector[1]
              yearx = datevector[2]
              article_date = datetime(int(yearx),int(monthx),int(dayx))
              hold_dict['date_publish'] = article_date
            else:
              contains_datelist = contains_date.split()
              for i in contains_datelist:
                if "201" in i:
                  indexdate = contains_datelist.index(i)
                else:
                  if "202" in i:
                    indexdate = contains_datelist.index(i)
              yearx = contains_datelist[indexdate] 
              dayx = contains_datelist[indexdate-2] 
              montht = contains_datelist[indexdate-1] 
              montht = montht.lower()
              monthx = months.index(montht) + 1
              article_date = datetime(int(yearx),int(monthx),int(dayx))
              hold_dict['date_publish'] = article_date
  except:
      article_date = None
      hold_dict['date_publish'] = None  

  return hold_dict 



# STEP 1: Creating URLs and inserting articles in the db
str_n = 1
end_n = 150000

url_count = 0
for i in range(str_n,end_n+1):
    url = "http://news.abamako.com/h/" + str(i) + ".html"
    print("Article no. ", str(i), " -- ", url)
    ## INSERTING IN THE DB:
    #time.sleep(1)
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
        article['source_domain'] = 'news.abamako.com' 
        article['language'] = 'fr'

        ## Fixing Date, Main Text and Title:
        response = requests.get(url, headers=header).text
        soup = BeautifulSoup(response)

        ## Date 
        article['date_publish'] = newsabamakocom_story(soup)['date_publish']

        ## Title
        article['title'] = newsabamakocom_story(soup)['title']

        ## Main Text
        article['maintext'] = newsabamakocom_story(soup)['maintext']

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
            print("Title: ", article['title'][0:25]," + Main Text: ", article['maintext'][0:30])
            #print(article['maintext'])
            print("Inserted! in ", colname, " - number of urls so far: ", url_count)
            db['urls'].insert_one({'url': article['url']})
        except DuplicateKeyError:
            print("DUPLICATE! Not inserted.")
    except Exception as err: 
        print("ERRORRRR......", err)
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")