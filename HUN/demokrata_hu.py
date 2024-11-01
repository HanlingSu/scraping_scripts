"""
Created on July 22 2022

@author: serkantadiguzel

This script scrapes/updates 'demokrata.hu' using sitemaps. 

Sitemaps are indexed from 1 to 122 [at the time of writing, September 20, 2022], so one can loop through the months to collect urls from the desired sitemaps. Smaller numbered sitemaps are older articles, so we can just get the ones greater than 122 in the next updates.

UPDATE (JAN 30, 2023): The sitemaps are no longer indexed from 1 to xxx. It is now put in bigger sitemaps and there are 13 of them. The last one is sitemap 13, which is scraped in this iteration. The next one scraping might include this one + 14 and bigger sitemaps.
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


db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p




headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

source = 'demokrata.hu'



# Custom Parser
def demokrata_story(soup):
    """
    Function to pull the information we want from hvg.hu stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    
    # get time
    publish_date = soup.find('time')['datetime']
    publish_date_final = dateparser.parse(publish_date, date_formats=['%Y-%m-%d %H:%M'])

    hold_dict['date_publish'] = publish_date_final
        
    # Get Highlighted Text:
    try:
        highlighted_text = soup.find('span', {'class': 'lead d-block'}).text.strip()
        if highlighted_text == '':
            highlighted_text = None         
    except:
        highlighted_text = None

    # Get Main Text:
    try:
        contains_maintext = soup.find("div", {"class":"postContent"})
        allowlist = ['p']
        text_elements = [t for t in contains_maintext.find_all(text=True) if t.parent.name in allowlist]
        maintext = ''.join(text_elements)
        maintext_final = maintext.strip()

    except: 
        maintext = None

    try:
        combined_text = highlighted_text + ' '+ maintext_final
        hold_dict['maintext'] = combined_text  
    except:
        combined_text = maintext_final
        hold_dict['maintext'] = combined_text

   
    return hold_dict





# baseurl = 'https://demokrata.hu/enews_article-sitemap'
# links = []
# for i in range(121, 123): ## UPDATE 
#     sitemapurl = baseurl + str(i) + '.xml'
#     print(sitemapurl)
#     reqs = requests.get(sitemapurl, headers=headers)
#     soup = BeautifulSoup(reqs.text, 'html.parser')
#     for link in soup.find_all('loc'):
#         links.append(link.text)


links = []
sitemapurl = 'http://demokrata.hu/wp-content/uploads/sitemap/enews_article_sitemap16.xml'
reqs = requests.get(sitemapurl, headers=headers)
soup = BeautifulSoup(reqs.text, 'html.parser')
for link in soup.find_all('loc'):
    links.append(link.text)



links = links.copy()
blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
links = [word for word in links if not blacklist.search(word)]

print('TOTAL LINKS:', len(links))

## INSERTING IN THE DB:
url_count = 0
for url in links[::-1]:
    print(url)
    if url == "":
        continue
    else:
        if url == None:
            continue
    
    try:
        response = requests.get(url, headers=headers)
        article = NewsPlease.from_url(url).__dict__
    except:
        time.sleep(0.5)
        try:
            response = requests.get(url, headers=headers)
            article = NewsPlease.from_url(url).__dict__
        except:
            continue

    
    soup = BeautifulSoup(response.text, 'html.parser')

       
    # add on some extras
    article['date_download']=datetime.now()
    article['download_via'] = "Direct2" #change
    article['source_domain'] = source

    # insert fixes from custom parser
    article['maintext'] = demokrata_story(soup)['maintext']
    article['date_publish'] = demokrata_story(soup)['date_publish']
    print(article['date_publish'])
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