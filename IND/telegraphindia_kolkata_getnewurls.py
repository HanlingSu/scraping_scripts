#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on March 16 2023

@author: bhumika

This script updates telegraphindia.com, Kolkata subsection
 
"""
# Packages:
import random
import sys
sys.path.append('../')
import os
import re
# from p_tqdm import p_umap
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
# from dotenv import load_dotenv
from bs4 import BeautifulSoup
# %pip install dateparser
import dateparser
import pandas as pd

import math

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


## NEED TO DEFINE SOURCE!
source = 'telegraphindia.com'

def telegraphindiacomkolkata_story(soup):
    """
    Function to pull the information we want from telegraphindia.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}

    # Get Title: 
    try:
        article_titlec = soup.find("meta", {"property":"og:title"})
        article_title = article_titlec["content"] 
        hold_dict['title']  = article_title
    except:
        try:
            article_title = soup.find("title").text
            hold_dict['title']  = article_title 
        except:
            hold_dict['title']  = None
        
    # Get Main Text:
    try:
        text = soup.find("article", {"class":"articlecontentbox"}).text.replace("ADVERTISEMENT\n\n\n", "")
        hold_dict['maintext'] = text
    except:
        hold_dict['maintext'] = None  

    # Get Date
    try:
        p_date = soup.find("div", {"class":"enpublicdate"}).text
        required_date = p_date.split("Published ")[1].split(", ")[0].split(".")
        article_date = datetime.strptime(required_date[0] + " " + required_date[1] + " " +required_date[2], "%d %m %y")
        hold_dict['date_publish'] = article_date
    except:
        hold_dict['date_publish'] = None
    
    return hold_dict 


urlsections = ["https://www.telegraphindia.com/my-kolkata", "https://www.telegraphindia.com/my-kolkata/news/page-", 
              "https://www.telegraphindia.com/my-kolkata/places/page-", "https://www.telegraphindia.com/my-kolkata/people/page-"]


for baseurl in urlsections:
  urls = []
  if baseurl == "https://www.telegraphindia.com/my-kolkata":
      url = baseurl
      req = requests.get(url, headers = headers)
      soup = BeautifulSoup(req.content, 'html.parser')
      for link in soup.find_all('a'):
          urls.append(link.get('href'))
  else:
      for j in range(1,1000):
          url = baseurl + str(j)
          req = requests.get(url, headers = headers)
          soup = BeautifulSoup(req.content, 'html.parser')
          if soup.find("div", {"class": "section_404"}):
            break 
          for link in soup.find_all('a'):
              urls.append(link.get('href'))


  blpatterns = ['/sports/','/entertainment/','/gallery/']
  clean_urls = []
  for url in urls:
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
                  if not "https://www.telegraphindia.com/" in url:
                      url = "https://www.telegraphindia.com/" + url
                  clean_urls.append(url)
      
  list_urls = list(set(clean_urls))
  print("Total number of USABLE urls found: ", len(list_urls))


  ## INSERTING IN THE DB:
  url_count = 0
  final_section_incorrect_data = []
  final_section_data = []
  for url in list_urls:
      ## SCRAPING USING NEWSPLEASE:
      try:
          #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
          header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
          response = requests.get(url, headers=header)
          # process
          article = NewsPlease.from_html(response.text, url=url).__dict__
          # add on some extras
          article['date_download'] = datetime.now()
          article['download_via'] = "LocalIND"
          article['source_domain'] = source 
          
          #if '/en/' in url:
          #    article['language'] = 'en'
          #article['language'] = 'es'
          
          ## Fixing Date + Title + Main Text
          soup = BeautifulSoup(response.content, 'html.parser')
          article['date_publish'] = telegraphindiacomkolkata_story(soup)['date_publish']
          article['title'] = telegraphindiacomkolkata_story(soup)['title']
          article['maintext'] = telegraphindiacomkolkata_story(soup)['maintext']
          final_section_data.append(article)

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
          except:
              colname = 'articles-nodate'
          try:
              url_count = url_count + 1
              # # Inserting article into the db:
              db[colname].insert_one(article)
              # print(" + Date: ", article['date_publish'], " + Main Text: ", article['maintext'][0:50], " + Title: ", article['title'][0:25])
              # print("Inserted! in ", colname, " - number of urls so far: ", url_count)
              db['urls'].insert_one({'url': article['url']})
          except DuplicateKeyError as err:
              print("DUPLICATE! Not inserted.")
      except Exception as err: 
          final_section_incorrect_data.append({'url': url, "err": err})
          print("ERRORRRR......", err)
          pass

  print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")