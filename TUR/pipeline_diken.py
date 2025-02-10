"""
Created on August 16 2022

@author: serkantadiguzel

This script scrapes/updates 'diken.com.tr' using sitemaps. 
Each sitemap has around 1000 URLs, so in each update we need to change the numbers below. 

No section information is recorded in urls so it is not possible to blacklist sections.

""" 
 
import random
import sys
import os
import re
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from pymongo.errors import CursorNotFound
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date, timedelta
from newsplease import NewsPlease
from datetime import datetime
import dateparser
import time


# db connection
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p


# Each sitemap includes 1000 links. Currently there are 165. In the next update, we can scrape only those between 1 and x-166 where x is the biggest sitemap number available. 
start_sitemap = 1 #CHANGE
end_sitemap = 7 #CHANGE



headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

source = 'diken.com.tr'


base_url = 'https://www.diken.com.tr/post-sitemap'
# base_url = 'https://www.diken.com.tr/wp-sitemap-posts-post-'
links = []
for i in range(start_sitemap, end_sitemap):
    
    sitemap_url = base_url + str(i) + '.xml'
    if i==1:
        sitemap_url = base_url + '.xml'
    print('Getting sitemap:', sitemap_url)
    reqs = requests.get(sitemap_url, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    for link in soup.find_all('loc'):
        links.append(link.text)

links = list(set(links))

print('Total Links collected:', len(links))

# Custom Parser
def dikencomtr_story(soup):
    """
    Function to pull the information we want from diken.com.tr stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}

    # Get Title: 
    try:
        contains_title = soup.find("h1", {"class":"entry-title"})
        article_title = contains_title.text.strip()
        hold_dict['title']  = article_title   
    except:
        try:
            contains_title = soup.find("h2", {"class":"entry-title"})
            article_title = contains_title.text.strip()
            hold_dict['title']  = article_title 
        except:
            article_title = None
            hold_dict['title']  = None
        

    # Get Main Text:
    try:
        contains_maintext = soup.find("div", {"class":"entry-content"})
        maintext = contains_maintext.text.strip()
        hold_dict['maintext'] = maintext
    except: 
        maintext = None
        hold_dict['maintext'] = maintext

       

    # Get Date
    try:
        contains_date = soup.find("time", {"class":"entry-time"})
        contains_date = contains_date.attrs['datetime']
        article_date = dateparser.parse(contains_date, date_formats=['%d/%m/%Y %H:%M'])
        article_date = article_date.replace(tzinfo=None)
        hold_dict['date_publish'] = article_date 
    except:
        hold_dict['date_publish'] = None
   
    return hold_dict



## INSERTING IN THE DB:
url_count = 0
for url in links:
    if url == "":
        continue
    else:
        if url == None:
            continue
    
    try:
        response = requests.get(url, headers=headers)
    except:
        time.sleep(0.5)
        try:
            response = requests.get(url, headers=headers)
        except:
            continue
    try:    
        article = NewsPlease.from_html(response.text).__dict__
        soup = BeautifulSoup(response.text, 'html.parser')
    except ValueError:
        continue

       
    # add on some extras
    article['date_download']=datetime.now()
    article['download_via'] = "Direct2" #change
    article['source_domain'] = source
    article['url'] = url #I switched to newsplease.form_html to do 1 request for each url.

    # insert fixes from custom parser
    article['title'] = dikencomtr_story(soup)['title']
    article['maintext'] = dikencomtr_story(soup)['maintext']
    article['date_publish'] = dikencomtr_story(soup)['date_publish']

    ## Inserting into the db
    try:
        year = article['date_publish'].year
        month = article['date_publish'].month
        colname = f'articles-{year}-{month}'
        #print(article)
    except:
        colname = 'articles-nodate'

    try:
        # Inserting article into the db:
        db[colname].insert_one(article)
        # count:
        url_count = url_count + 1

        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
    except DuplicateKeyError:
        print("DUPLICATE! Not inserted.")




print("Done inserting ", url_count, "collected urls from ",  source, " into the db.")