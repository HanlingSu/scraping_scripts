import os
import sys
import re
import json
import time
import random
import getpass
import urllib.request
from urllib.parse import quote_plus, urlparse

import numpy as np
import pandas as pd
from pandas.core.common import flatten
from tqdm import tqdm

from datetime import timedelta, date, datetime
from dateutil.relativedelta import relativedelta
import dateparser
from dateparser.search import search_dates

import requests
import cloudscraper
from bs4 import BeautifulSoup, SoupStrainer
import bs4

from newspaper import Article
import newspaper
from newsplease import NewsPlease

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, CursorNotFound

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from dotenv import load_dotenv

from warnings import warn

db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# Selenium collecting direct URLs
direct_URLs = set()
page = 0
souce = "dailypakistan.com.pk"
url = 'https://dailypakistan.com.pk/environment'
driver = webdriver.Chrome() 


print(url)
driver.get(url)    
time.sleep(3)
while page<100000:
    try:
        xpath = '//*[@id="post_show_more"]'
        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        driver.execute_script("arguments[0].scrollIntoView();", element)
        
        element.click()  
        time.sleep(1)

        page+=1
        print('Page {}'.format(page))
        
        
    except:
        # Break if button is not found
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        
        # page+=1
        print('No button')
        pass
        #Give enough time for button and urls to appear
    
    if page % 5 == 0:
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            for item in soup.find_all('h3'):
                try:
                    direct_URLs.add(item.find('a')['href'])
                except:
                    pass
                    print("no item")
            print(len(direct_URLs))
            
        except:
            print('No soup')
        time.sleep(3)

        

# Parse dorect URLs using selenium

url_count = 0
processed_url_count = 0
final_result_len = 0
    

final_result_len += len(direct_URLs)

driver = webdriver.Chrome() 

for url in direct_URLs:
    if url:
        print(url, "FINE")

        
        print(url)
        ## SCRAPING USING NEWSPLEASE:
        try:

            # process
            driver.get(url) 
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            article = NewsPlease.from_html(driver.page_source).__dict__
            
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            article['url'] = url
            article['environmental'] = True

           
            print("newsplease maintext: ", article['maintext'][:50])
            print("newsplease date: ", article['date_publish'])
            print("newsplease title: ", article['title'])

            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'articles-{year}-{month}'
            except:
                colname = 'articles-nodate'
            try:
                
                db[colname].insert_one(article)
                # count:
                if colname!= 'articles-nodate':
                    url_count = url_count + 1
                    print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                    db['urls'].insert_one({'url': article['url']})
            except DuplicateKeyError:
                print("DUPLICATE! Not inserted.")
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', final_result_len, 'articles have been processed ...\n')

    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
