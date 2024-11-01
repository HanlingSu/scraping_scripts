"""
Created on Nov 1 2022

@author: serkantadiguzel

This script scrapes/updates 'podrobno.uz'.

It scraped from sitemaps but note that the numbering of sitemaps is weird. One should check next time we update this source.

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



headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

pages = [35, 38, 39, 40, 41, 42] # This might be updated when we want to update the source. We should check!


source = 'podrobno.uz'


base_url = 'https://podrobno.uz/sitemap-iblock-'
links = []
for i in pages:
    sitemap_url = base_url + str(i) + '.xml'
    print('Getting sitemap:', sitemap_url)
    reqs = requests.get(sitemap_url, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    for link in soup.find_all('loc'):
        links.append(link.text)
    

sitemap_url_custom = "https://podrobno.uz/sitemap-iblock-35.part1.xml"
reqs_custom = requests.get(sitemap_url_custom, headers=headers)
soup_custom = BeautifulSoup(reqs_custom.text, 'html.parser')
for link in soup_custom.find_all('loc'):
    links.append(link.text)


links = list(set(links))

print('Total Links collected:', len(links))

# Custom Parser
def podronouz_story(soup):
    """
    Function to pull the information we want from podrobno.uz stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
       

    # Get Date
    try:
        contains_date = soup.find("time", {"class":"entry-date published updated"})
        article_date = dateparser.parse(contains_date.text)
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
    article['url'] = url 

    # insert fixes from the custom parser
    try:
        article['maintext'] =  article['maintext'].replace('Узбекистан, Ташкент - AH Podrobno.uz.', '')
    except AttributeError:
        pass

    article['date_publish'] = podronouz_story(soup)['date_publish']

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