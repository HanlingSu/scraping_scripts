#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Nov 1 2021

@author: diegoromero

This script updates newsghana.com.gh -- it must be edited to 
scrape the most recent articles published by the source.

It needs to be run everytime we need to update GHA sources. 
The most recent stuff is found as the page number increases. So next time, we need to increase the numbers below for sitemaps.

"""
# Packages:
from pymongo import MongoClient
from bs4 import BeautifulSoup
from dateparser.search import search_dates
import dateparser
import requests
from urllib.parse import quote_plus
import time
from datetime import datetime
from pymongo.errors import DuplicateKeyError
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from dotenv import load_dotenv


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


## COLLECTING URLS
direct_URLs = []

## NEED TO DEFINE SOURCE!
source = 'dailyguidenetwork.com'

## STEP 0: URLS FROM SITEMAP:

beginnumber = 93
endnumber = 95

for i in range(beginnumber, endnumber+1):
    url = "https://dailyguidenetwork.com/post-sitemap" + str(i) + ".xml"
    print("Extracting from: ", url)
    reqs = requests.get(url, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    for link in soup.findAll('loc'):
        direct_URLs.append(link.text)
    #for link in soup.find_all('a'):
    #    urls.append(link.get('href')) 
    print(len(direct_URLs))

# List of unique urls:
final_result = direct_URLs.copy()

print("Total number of urls found: ", len(final_result))



## INSERTING IN THE DB:
url_count = 0
processed_url_count = 0
for url in final_result[::-1]:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if "https://dailyguidenetwork.com" in url:
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
                    
                    ## Fixing Date:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Get Date
                    try: 
                        contains_date = soup.find("meta", {"property":"article:published_time"})
                        contains_date = contains_date["content"]
                        article_date = dateparser.parse(contains_date, date_formats=['%d/%m/%Y'])
                        article['date_publish'] = article_date
                    except:
                        article_date = article['date_publish']
                        article['date_publish'] = article_date
                    print('Date: ',article['date_publish'])

                    # Get Main Text:
                    try:
                        maintext_contains = soup.find('div', {'class' : 'post-entry'}).find_all('p')
                        maintext = ''
                        for i in maintext_contains:
                            maintext += i.text
                        article['maintext'] = maintext.strip()
                    except: 
                        maintext = article['maintext']
                        article['maintext'] = maintext
                    print('Maintext: ', article['maintext'][:50])

                    # Get Title:
                    try:
                        #article_title = soup.find("title").text
                        contains_article = soup.find("meta", {"property":"og:title"}).find_all('p')
                        article_title = contains_article['content']
                        article['title']  = article_title   
                    except:
                        article_title = article['title']
                        article['title'] = article_title
                    print('Title: ',article['title'])
                    
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
                        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        #db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        print("DUPLICATE! Not inserted.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
                processed_url_count += 1
                print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')
 
            else:
                pass


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
