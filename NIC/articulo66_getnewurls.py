#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Apr 2 2021

@author: diegoromero

This script updates 'articulo66.com' using section sitemaps.
You can run this script as often as you want.
 
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
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


## COLLECTING URLS
urls = []

## NEED TO DEFINE SOURCE!
source = 'articulo66.com'

# Custom Parser:
def articulo66_story(soup):
    """
    Function to pull the information we want from articulo66.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    # create a dictionary to hold everything in
    hold_dict = {}
    
    # Get Title: 
    try:
        article_title = soup.find("title").text
        hold_dict['title']  = article_title   

    except:
        hold_dict['title']  = None
        
    # Get Main Text:
    try:
        #maintext = soup.find('p', attrs={'class':'entry-excerpt entry-excerpt-content-custom'}).text
        contains_text = soup.findAll('p')
        if len(contains_text) > 1:
            maintext = ''
            for i in contains_text:
                maintext += i.text
            
            if "Publicado el" in maintext:
                maintext = maintext[12:]
            hold_dict['maintext'] = maintext
    except: 
        hold_dict['maintext']  = None

    # Get Date:
    #meta property="article:published_time" content="2022-04-02T16:26:32+00:00"
    try:
        contains_date = soup.find("meta", {"property": "article:published_time"})
        article_date = dateparser.parse(contains_date['content'])
        hold_dict['date_publish'] = article_date  

    except:
        article_date = None
        hold_dict['date_publish'] = None  

    return hold_dict 

# STEP 0: URLs from the "todas-nuestras-noticias" section
sections = ['politica','nacionales','internacionales']
endnumbers = [37,42,35]

#https://www.articulo66.com/categorias/politica/
#https://www.articulo66.com/categorias/politica/page/906/
#https://www.articulo66.com/categorias/nacionales/
#https://www.articulo66.com/categorias/nacionales/page/1109/
#https://www.articulo66.com/categorias/internacionales/
#https://www.articulo66.com/categorias/internacionales/page/475/

for section in sections:
    indexword = sections.index(section)
    endnumberx = endnumbers[indexword]

    for i in range(1,endnumberx+1):
        if i == 1:
            url = 'https://www.articulo66.com/categorias/' + section + '/'
        else:
            url = 'https://www.articulo66.com/categorias/' + section + '/page/' + str(i) + '/'

        print("URL: ", url)

        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        for link in soup.find_all('h3', {'class' : 'jeg_post_title'}):
                urls.append(link.find('a')['href']) 
        
        print("URLs so far: ", len(urls))

# KEEP ONLY unique URLS:
dedupurls = list(set(urls))

#dftest = pd.DataFrame(urls)  
#dftest.to_csv('/Users/diegoromero/Downloads/test.csv')  

# STEP 3: Get rid or urls from blacklisted sources
# blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
# blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
# dedupurls = [word for word in dedupurls if not blacklist.search(word)]


list_urls = dedupurls.copy()
print("Total number of USABLE urls found: ", len(list_urls))


## INSERTING IN THE DB:
url_count = 0
processed_url_count = 0
for url in list_urls:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if 'articulo66.com' in url:
                print(url, "FINE")
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
                    article['source_domain'] = 'articulo66.com'
                    
                     ## Fixing what needs to be fixed:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # TITLE:
                    if article['title'] == None:
                        try:
                            article['title'] = articulo66_story(soup)['title']
                        except:
                            article['title'] == None
                    print("newsplease title: ", article['title'])
                    
                    # MAIN TEXT:
                    if article['maintext'] == None:
                        try:
                            article['maintext'] = articulo66_story(soup)['maintext']
                        except:
                            article['maintext'] == None
                    if  article['maintext']:
                        print("newsplease maintext: ", article['maintext'][:50])

                    # Fixing date:
                    if article['date_publish'] == None:
                        try:
                            article['date_publish'] = articulo66_story(soup)(soup)['date_publish']
                        except:
                            article['date_publish'] == None
                    print("newsplease date: ", article['date_publish'])
                    
                    #article['date_publish'] = nuevayacomni_story(soup)['date_publish']

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
                        if colname != 'articles-nodate':
                            url_count = url_count + 1
                            print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        print("DUPLICATE! Not inserted.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
                processed_url_count += 1
                print('\n',processed_url_count, '/', len(list_urls), 'articles have been processed ...\n')

            else:
                pass


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")