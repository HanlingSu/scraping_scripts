#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Nov 11 2021

@author: bhumika

This script updates naiduniya.com 
 
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
from dotenv import load_dotenv
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
source = 'naidunia.com'

monthupdate = 3
yearupdate = 2023

def naiduniya_story(soup):
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
        text = soup.find("p").text
        hold_dict['maintext'] = text.strip()
    except:
        hold_dict['maintext'] = None  

    # Get Date
    try:
        containsdate = soup.find("span", {"class":"fl date"}).text
        datevector = containsdate.split(", ")
        datevector = datevector[1].split(" ")
        dayx = datevector[0]
        monthx = datevector[1]
        year = datevector[2]
        final_date = dayx + " " + monthx + " " + year

        article_date = datetime.strptime(final_date, "%d %b %Y")
        hold_dict['date_publish'] = article_date
    except Exception as err:
        hold_dict['date_publish'] = None
        print("Error when trying to get the date", err)

    return hold_dict


section_sitemap = "https://www.naidunia.com/web-sitemap-nd.xml"
req = requests.get(section_sitemap, headers = headers)
soup = BeautifulSoup(req.content)
sections_URLs = []
for i in soup.find_all('loc'):
    sections_URLs.append(i.text)
print('Now collected',len(sections_URLs), 'section URLs')

# Parse each direct url now
blpatterns = ['/sports','/entertainment','/horoscope-rashifal', '/spiritual', '/contact-us', '/privacy-policy', 
                '/advertise-withus', '/about-us', 'javascript:', 'mailto:']
count = 0
for section_url in sections_URLs:
    section_inner_urls = set()

    # Step 1: obtain urls in each section paginated page
    for j in range(1,400):
        url_to_parse = section_url + "-page" + str(j)
        print('working on: ', url_to_parse)
        req = requests.get(url_to_parse, headers = headers)
        soup = BeautifulSoup(req.content, 'html.parser')

        for link in soup.find_all('a'):
            section_inner_urls.add(link.get('href')) 

    print('Now collected ',len(section_inner_urls), 'section inner URLs for last j: ', j)

    # Step 2: clean urls in each section paginated page according to blacklist
    section_clean_urls = set()
    for url in section_inner_urls:
        if url == "" or url == None:
            continue

        for pattern in blpatterns:
            if pattern in url:
                break
        else:
            if not "https://www.naidunia.com/" in url and not "https:" in url:
                url = "https://www.naidunia.com" + url
            section_clean_urls.add(url)
    print('Now collected ',len(section_clean_urls), 'section clean inner URLs')

    # Step 3: obtain html details from the cleaned section urls
    url_count = 0
    for section_clean_url in section_clean_urls:
        ## SCRAPING USING NEWSPLEASE:
        try:
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            response = requests.get(section_clean_url, headers=header)

            # process
            article = NewsPlease.from_html(response.text, url=section_clean_url).__dict__
            article['date_download'] = datetime.now()
            article['download_via'] = "LocalIND"
            article['source_domain'] = source

            soup = BeautifulSoup(response.content, 'html.parser')

            extracted_data = naiduniya_story(soup)

            article['date_publish'] = extracted_data['date_publish']
            article['title'] = extracted_data['title']
            article['maintext'] = extracted_data['maintext']

            # Define collection to update:
            colname_toupdate = f'articles-{yearupdate}-{monthupdate}'
            # final_section_data.append(article)
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'articles-{year}-{month}'
            except:
                colname = 'articles-nodate'
            try:
                if colname == colname_toupdate:
                    url_count = url_count + 1
                    #Inserting article into the db:
                    db[colname].insert_one(article)
                    print(" + Date: ", article['date_publish'], " + Main Text: ", article['maintext'][0:50], " + Title: ", article['title'][0:25])
                    print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                else:
                    print("Not in desired collection.")
            except DuplicateKeyError:
                print("DUPLICATE! Not inserted for section clean url : ", section_clean_url)

        except Exception as err:
            print("Exception in section clean url : ", section_clean_url)
            print("ERRORRRR......", err)
            # final_section_incorrect_data.append({'url': section_clean_url, "err": err})

    print("Done inserting ", url_count, " for section ", section_url ," manually collected urls from ",  source, " into the db.")