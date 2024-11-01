#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Nov 1 2021

@author: diegoromero

This script updates ghanaweb.com -- it must be edited to 
scrape the most recent articles published by the source.

It needs to be run everytime we need to update GHA sources. 

UPDATE SERKANT (NOV 28, 2022): The following part no longer chooses the section to gather URLs, so I changed it "soup.find_all('ul', {'margin-left':"40px"})):"

UPDATE Serkant (APRIL 17, 2023): Sitemaps have changed. There now seems to be monthly sitemaps, which I use below. Also we needed an update in headers. See below for the updated header.

"""
# Packages:
from cgi import print_arguments
from glob import escape
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
#headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# without a cookie, it throws an error.
headers = {'Cookie': '_cb=QTqlM1frFCBJSK2J; _chartbeat2=.1681737092292.1681737804001.1.BTAV68BpRICACqL1QtBRUeFBtD_QO.3; _ga=GA1.2.765761989.1681737075; _ga_MMETNYQCKH=GS1.1.1681737075.1.1.1681737804.60.0.0; _gid=GA1.2.1753295471.1681737075; AWPR0F=0296258359920%230796661108739%2301TR%23050%23f2a911bc252187%23f00%2300d%23f176040%23113%23ffdde9ed76fa9ec12%23104%23304%233a1%23201; GEOP=TR%2C+%2C745044; LND=TR; MBR=40db8e9c404c750392840bd88f1d0bac',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Host': 'www.ghanaweb.com',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15',
'Accept-Language': 'en-US,en;q=0.9',
'Connection': 'keep-alive'
}



## COLLECTING URLS
direct_URLs = []

## NEED TO DEFINE SOURCE!
source = 'ghanaweb.com'

## STEP 1: URLS FROM THE WEBSITE'S DAYLY ARCHIVE

# url = 'https://www.ghanaweb.com/GhanaHomePage/NewsArchive/browse.archive.php?date=20221010'
# reqs = requests.get(url, headers=headers)
# soup = BeautifulSoup(reqs.text, 'html.parser')
# for i in soup.find_all('div', {'class':"left_artl_list more_news"}):
#     for j in i.find_all('li'):
#        print(j.find('a')['href'])
       

# # example url: https://www.ghanaweb.com/GhanaHomePage/NewsArchive/browse.archive.php?date=20211101

# for year in range(2022, 2023):
#     yearstr = str(year)
#     for month in range(11, 13):
#         if month < 10:
#             monthstr = '0' + str(month)
#         else:
#             monthstr = str(month)
#         print('Now scraping ', yearstr, monthstr, 'news  ...  ')
#         for day in range(1, 32):
#             if day < 10:
#                 daystr = '0' + str(day)
#             else:
#                 daystr = str(day)

#             url = 'https://www.ghanaweb.com/GhanaHomePage/NewsArchive/browse.archive.php?date=' + yearstr + monthstr + daystr
#             # print("Getting urls from: ",url)
#             reqs = requests.get(url, headers=headers)
#             soup = BeautifulSoup(reqs.text, 'html.parser')

#             for i in soup.find_all('div', {'class':"left_artl_list more_news"}):
#                 for j in i.find_all('li'):
#                     direct_URLs.append(j.find('a')['href'])
#         print('Now scraped ', len(direct_URLs), 'articles from previous months ... ')
#             #for link in soup.findAll('loc'):
#                 #urls.append(link.text)


for year in range(2024, 2025):
    yearstr = str(year)
    for month in range(7, 11):
        if month < 10:
            monthstr = '0' + str(month)
        else:
            monthstr = str(month)

        url = 'https://www.ghanaweb.com/sitemaps/articles.xml?date=' + yearstr + monthstr

        print("Getting urls from: " , url)
        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        for link in soup.findAll('loc'):
            #print(link.text)
            direct_URLs.append(link.text)




# List of unique urls:
#final_result = ['https://www.ghanaweb.com' + i for i in direct_URLs]
final_result = list(set(direct_URLs))


print("Total number of urls found: ", len(final_result))


## INSERTING IN THE DB:
url_count = 0
processed_url_count = 0
for url in final_result:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if "ghanaweb.com" in url:
                print(url, "FINE")
                ## SCRAPING USING NEWSPLEASE:
                try:

                    response = requests.get(url, headers=headers)
                    # process
                    article = NewsPlease.from_html(response.text, url=url).__dict__
                    # add on some extras
                    article['date_download']=datetime.now()
                    article['download_via'] = "Direct2"
                    
                    ## Fixing Date:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    try:
                        contains_date = soup.find("meta", {"property":"article:published_time"})
                        contains_date = contains_date["content"]
                        article_date = dateparser.parse(contains_date, date_formats=['%d/%m/%Y'])
                        article['date_publish'] = article_date
                    except:
                        article_date = article['date_publish']
                        article['date_publish'] = article_date
                    print(article['date_publish'])
                    # Get Main Text:
                    try:
                        maintext = soup.find("p", {"style": "clear:right"}).text
                        article['maintext'] = maintext
                    except: 
                        maintext = article['maintext']
                        article['maintext'] = maintext
                    print(article['maintext'][:50])
                    # Get Title:
                    try:
                        article_title = soup.find('title').text
                        article['title'] = article_title
                    except: 
                        title = article['title']
                        article['title'] = title      
                    print(article['title'])
                 

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
                        db['urls'].insert_one({'url': article['url']})
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




