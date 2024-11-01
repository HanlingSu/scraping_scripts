"""
Created on August 16 2022

@author: serkantadiguzel

This script scrapes/updates 't24.com.tr' using sitemaps. 

Each day is stored in another sitemap, one can loop through the days to collect urls from the desired sitemaps.

It can be run as often as one desires once start and end date is updated below
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


# db connection: THIS LINE WILL CHANGE ONCE WE HAVE A NEW DB WORKING AT PENN
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

# CHANGE: Start date and end date can be updated here.
start_date = date(2023, 1, 1) 
end_date = date(2023, 3, 31) #change


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

source = 't24.com.tr'

base_url = 'https://media-cdn.t24.com.tr/media/sitemaps/sitemap-'
links = []

for single_date in daterange(start_date, end_date):
    single_day = single_date.strftime('%Y%m%d')
    sitemap_url = base_url + str(single_day)+ '.xml'
    print('Getting sitemap:', sitemap_url)
    reqs = requests.get(sitemap_url, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    for link in soup.find_all('loc'):
        links.append(link.text)




# blacklisted sections here
blacklist = ['/foto-haber/']

clean_urls = []
for link in links:
    if not any(x in link for x in blacklist):
        print(link,':', 'not blacklisted')
        clean_urls.append(link)
    

clean_urls = list(set(clean_urls))

print('Total Links collected:', len(clean_urls))


# Custom Parser
def t24comtr_story(soup):
    """
    Function to pull the information we want from t24.com.tr stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}

    # Get Title: 
    try:
        contains_title = soup.find("meta", {"property":"og:title"})
        article_title = contains_title['content']
        hold_dict['title']  = article_title.strip()   
    except:
        article_title = None
        hold_dict['title']  = None
        
    # Get Highlighted Text:
    try:
        highlighted_text = soup.find('h2').text.strip()
        if highlighted_text == '':
            highlighted_text = None         
    except:
        highlighted_text = None

    # Get Main Text:
    try:
        contains_maintext = soup.find("div", {"class":"_1NMxy"})
        maintext = contains_maintext.text.strip()
        
    except: 
        maintext = None

    try:
        combined_text = highlighted_text + '. '+ maintext
        hold_dict['maintext'] = combined_text  
    except:
        combined_text = maintext
        hold_dict['maintext'] = combined_text

    # Get Date
    try:
        contains_date = soup.find("div", {"class":"_392lz"})
        contains_date = contains_date.text
        #article_date = dateparser.parse(contains_date,date_formats=['%d/%m/%Y'])
        article_date = dateparser.parse(contains_date, languages = ['tr'])
        hold_dict['date_publish'] = article_date 
    except:
        hold_dict['date_publish'] = None
   
    return hold_dict



## INSERTING IN THE DB:
url_count = 0
for url in clean_urls:
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
    article['title'] = t24comtr_story(soup)['title']
    article['maintext'] = t24comtr_story(soup)['maintext']
    article['date_publish'] = t24comtr_story(soup)['date_publish']

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