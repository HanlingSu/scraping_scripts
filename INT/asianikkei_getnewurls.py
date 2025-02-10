#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on July 22 2022

@author: diegoromero

This script updates 'asia.nikkei.com' using sitemaps.
It can be run as often as one desires. 

MAKE SURE YOU REVISE ALL THE URLS FROM WHICH YOU ARE SCRAPING!
 
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
#db = MongoClient('mongodb://ml4pAdmin:ml4peace@research-devlab-mongodb-01.oit.duke.edu').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


## DEFINE SOURCE:
source = 'asia.nikkei.com'

## Define YEAR and MONTH to update:
year_up = 2024
month_up = 12

# Custom Parser
def asianikkeicom_story(soup):
    """
    Function to pull the information we want from asia.nikkei.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}

    # Get Title: 
    try:
        contains_title = soup.find("meta", {"property":"og:title"})
        article_title = contains_title['content']
        hold_dict['title']  = article_title   
    except:
        article_title = None
        hold_dict['title']  = None
        
    # Get Main Text:
    try:
        contains_maintext = soup.find("meta", {"property":"og:description"})
        maintext = contains_maintext['content']
        hold_dict['maintext'] = maintext  
    except: 
        maintext = None
        hold_dict['maintext']  = None

    # Get Date
    try:
        contains_date = soup.find("meta", {"name":"date"})
        contains_date = contains_date['content']
        #article_date = dateparser.parse(contains_date,date_formats=['%d/%m/%Y'])
        article_date = dateparser.parse(contains_date)
        hold_dict['date_publish'] = article_date 
    except:
        hold_dict['date_publish'] = None
   
    return hold_dict 

## STEP 1: COLLECTING URLS FROM KEYWORD SEARCHES:
# keywords:
keywords = ['Afghanistan','Albania','Algeria','Andorra','Angola','Antigua+and+Barbuda','Argentina','Armenia','Australia','Austria','Azerbaijan','Bahamas','Bahrain','Bangladesh','Barbados','Belarus','Belgium','Belize','Benin','Bhutan','Bolivia','Bosnia+and+Herzegovina','Botswana','Brazil','Brunei','Bulgaria','Burkina+Faso','Burundi','Côte+d%27Ivoire','Cabo+Verde','Cambodia','Cameroon','Canada','Central+African+Republic','Chad','Chile','China','Colombia','Comoros','Congo','Costa+Rica','Croatia','Cuba','Cyprus','Czechia','Czech+Republic','Denmark','Djibouti','Dominica','Dominican+Republic','Ecuador','Egypt','El+Salvador','Equatorial+Guinea','Eritrea','Estonia','Eswatini','Ethiopia','Fiji','Finland','France','Gabon','Gambia','Georgia','Germany','Ghana','Greece','Grenada','Guatemala','Guinea','Guinea-Bissau','Guyana','Haiti','Vatican','Honduras','Hungary','Iceland','India','Indonesia','Iran','Iraq','Ireland','Israel','Italy','Jamaica','Japan','Jordan','Kazakhstan','Kenya','Kiribati','Kuwait','Kyrgyzstan','Laos','Latvia','Lebanon','Lesotho','Liberia','Libya','Liechtenstein','Lithuania','Luxembourg','Madagascar','Malawi','Malaysia','Maldives','Mali','Malta','Marshall+Islands','Mauritania','Mauritius','Mexico','Micronesia','Moldova','Monaco','Mongolia','Montenegro','Morocco','Mozambique','Myanmar','Namibia','Nauru','Nepal','Netherlands','New+Zealand','Nicaragua','Niger','Nigeria','North+Korea','North+Macedonia','Norway','Oman','Pakistan','Palau','Palestine','Panama','Papua+New+Guinea','Paraguay','Peru','Philippines','Poland','Portugal','Qatar','Romania','Russia','Rwanda','Saint+Kitts+and+Nevis','Saint+Lucia','Samoa','San+Marino','Sao+Tome+and+Principe','Saudi+Arabia','Senegal','Serbia','Seychelles','Sierra+Leone','Singapore','Slovakia','Slovenia','Solomon+Islands','Somalia','South+Africa','South+Korea','South+Sudan','Spain','Sri+Lanka','Sudan','Suriname','Sweden','Switzerland','Syria','Tajikistan','Tanzania','Thailand','Timor-Leste','Togo','Tonga','Trinidad+and+Tobago','Tunisia','Turkey','Turkmenistan','Tuvalu','Uganda','Ukraine','United+Arab+Emirates','UAE','United+Kingdom','Uruguay','Uzbekistan','Vanuatu','Venezuela','Vietnam','Yemen','Zambia','Zimbabwe','coup','arrest','journalist','press','press+freedom','activist','military','police','law',"corruption","bribe"]
#keywords = ['Guatemala','El+Salvador']
#https://www.csmonitor.com/content/search?SearchText=Egypt&SearchSectionID=-1&SearchDate=-1&sort=
#https://www.csmonitor.com/content/search/(offset)/30?SearchText=Egypt&SearchSectionID=-1&SearchDate=-1&sort=

for word in keywords:
    ## COLLECTING URLS
    urls = []

    initial_url = "https://asia.nikkei.com/search?contentType=article&query=" + word + "&sortBy=newest&facet%5B%5D=article_display_date_value_dt%3A%221month%22&dateFrom=&dateTo=&source=filter"
    print(initial_url)
    req = requests.get(initial_url, headers = headers)
    soup = BeautifulSoup(req.content, 'html.parser')

    # Obtaining number of pages:
    #soup.find("meta", {"name":"date"})
    allpages = soup.findAll("a", {"class":"pagination__item-link"})
    pagenumbers = []

    if allpages == []:
        # URLs from ONLY page:
        soup = BeautifulSoup(req.text, 'html.parser')
        #for link in soup.findAll('loc'):
        #    urls.append(link.text)
        for link in soup.find_all('a'):
            if link.get('href') == None:
                pass
            else:
                if "/about" in link.get('href'):
                    pass
                else:
                    if link.get('href') == "":
                        pass
                    else:
                        exturl = "https://asia.nikkei.com" + link.get('href')
                        urls.append(exturl) 
        print("URLs so far: ", len(urls))
    else:
        for page in allpages:
            if page.text != "":
                pagenumbers.append(int(page.text))
        end_page = max(pagenumbers)

        print(end_page, " pages about ", word)
        
        # URLs from first page:
        soup = BeautifulSoup(req.text, 'html.parser')
        #for link in soup.findAll('loc'):
        #    urls.append(link.text)
        for link in soup.find_all('a'):
            if link.get('href') == None:
                pass
            else:
                if "/about" in link.get('href'):
                    pass
                else:
                    if link.get('href') == "":
                        pass
                    else:
                        exturl = "https://asia.nikkei.com" + link.get('href')
                        urls.append(exturl) 
        print("URLs so far: ", len(urls))

        for i in range(2,end_page+1):
            url = "https://asia.nikkei.com/search?contentType=article&dateFrom=&dateTo=&facet%5B0%5D=article_display_date_value_dt%3A%221month%22&query=" + word + "&sortBy=newest&source=filter&page=" + str(i)

            print("+ + + Extracting from: ", url)
            reqs = requests.get(url, headers=headers)
            soup = BeautifulSoup(reqs.text, 'html.parser')
            #for link in soup.findAll('loc'):
            #    urls.append(link.text)
            for link in soup.find_all('a'):
                if link.get('href') == None:
                    pass
                else:
                    if "/about" in link.get('href'):
                        pass
                    else:
                        if link.get('href') == "":
                            pass
                        else:
                            exturl = "https://asia.nikkei.com" + link.get('href')
                            urls.append(exturl) 
            print("URLs so far: ", len(urls))

    # Manually check urls:
    #dftest = pd.DataFrame(list_urls)  
    #dftest.to_csv('/Users/diegoromero/Downloads/test.csv')  

    # STEP 2: Get rid or urls from blacklisted sources
    blpatterns = ['/Opinion/', '/Life-Arts/', '/Tea-Leaves/', '/Obituaries/']
    dedup = list(set(urls))
    print(len(dedup))
    list_urls = []
    for url in dedup:
        count_patterns = 0
        for pattern in blpatterns:
            if pattern in url:
                count_patterns = count_patterns + 1
        if count_patterns == 0:
            #newurl = "https://asia.nikkei.com" + url
            list_urls.append(url)

    print("Total number of USABLE urls found: ", len(list_urls))


    ## INSERTING IN THE DB:
    url_count = 0
    for url in list_urls:
        if url == "":
            pass
        else:
            if url == None:
                pass
            else:
                if 'asia.nikkei.com' in url:
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
                        article['source_domain'] = 'asia.nikkei.com'
                        
                        ## Fixing Date, Main Text and Title:
                        response = requests.get(url, headers=header).text
                        soup = BeautifulSoup(response)

                        ## Title
                        #article['title'] = asianikkeicom_story(soup)['title'] 
                        ## Main Text
                        #article['maintext'] = asianikkeicom_story(soup)['maintext'] 
                        ## Date
                        #article['date_publish'] = asianikkeicom_story(soup)['date_publish'] 

                        ## Inserting into the db
                        # collection to update:
                        colname_update = f'articles-{year_up}-{month_up}'

                        try:
                            year = article['date_publish'].year
                            month = article['date_publish'].month
                            colname = f'articles-{year}-{month}'
                            #print(article)
                        except:
                            colname = 'articles-nodate'
                        try:
                            if colname == colname_update:
                            # Inserting article into the db:
                                db[colname].insert_one(article)
                                # count:
                                url_count = url_count + 1
                                print("+TITLE: ", article['title'][0:20], " +MAIN TEXT: ", article['maintext'][0:25])
                                print("Date extracted: ", article['date_publish'], " + Inserted! in ", colname, " - number of urls so far: ", url_count)
                                db['urls'].insert_one({'url': article['url']})
                            else:
                                if colname == 'articles-nodate':
                                    # Inserting article into the db (articles-nodate collection):
                                    db[colname].insert_one(article)
                                    # count:
                                    print("+TITLE: ", article['title'][0:20], " +MAIN TEXT: ", article['maintext'][0:25])
                                    print("No date extracted. -> Inserted in ", colname)
                                    db['urls'].insert_one({'url': article['url']})
                                else:
                                    pass
                        except DuplicateKeyError:
                            print("DUPLICATE! Not inserted.")
                    except Exception as err: 
                        print("ERRORRRR......", err)
                        pass
                else:
                    pass


    print("Done inserting manually collected urls from ",  source, " into the db.")