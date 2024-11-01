#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 18 204

@author: Togbedji Gansey

This script updates 'themoscowtimes.com' using sitemaps.
It can be run as often as one desires. 
 
"""




import random
import sys
sys.path.append('../')
import os
import re
#from p_tqdm import p_umap
from tqdm import tqdm
from pymongo import MongoClient
import random

from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from pymongo.errors import CursorNotFound
import requests
# %pip install dateparser
import dateparser
import pandas as pd
from newsplease import NewsPlease

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Initialize Chrome WebDriver
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

## NEED TO DEFINE SOURCE!
source = 'naidunia.com'
# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

def scroll_to_bottom(driver):

    old_position = 0
    new_position = None

    while new_position != old_position:
        # Get old scroll position
        old_position = driver.execute_script(
                ("return (window.pageYOffset !== undefined) ?"
                 " window.pageYOffset : (document.documentElement ||"
                 " document.body.parentNode || document.body);"))
        # Sleep and Scroll
        time.sleep(3)
        driver.execute_script((
                "var scrollingElement = (document.scrollingElement ||"
                " document.body);scrollingElement.scrollTop ="
                " scrollingElement.scrollHeight;"))
        # Get new position
        new_position = driver.execute_script(
                ("return (window.pageYOffset !== undefined) ?"
                 " window.pageYOffset : (document.documentElement ||"
                 " document.body.parentNode || document.body);"))

def scroll_up(driver):
    # Get current scroll position
    old_position = driver.execute_script(
        "return (window.pageYOffset !== undefined) ? window.pageYOffset : (document.documentElement || document.body.parentNode || document.body);"
    )

    # Calculate new scroll position to scroll up a little bit (e.g., 600 pixels)
    new_position = max(old_position + 600, 0)

    # Scroll up
    driver.execute_script(
        f"window.scrollTo({{ top: {new_position}, behavior: 'smooth' }});"
    )

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# STEP 0: Get sitemap urls:
def sitemap_category(url):
    blacklisted = ['/latest-news','/special-story','/sports/', '/entertainment/', '/bollywood', '/technology/', '/spiritual/', '/horoscope-rashifal/', '/about-us', '/advertise-withus', '/privacy-policy', '/contact-us', '/sports', '/entertainment', '/bollywood/', '/technology', '/spiritual', '/horoscope-rashifal']
    siteurls = []

    # Send a GET request to the sitemap URL
    reqs = requests.get(url, headers=headers)
    
    # Parse the response content using BeautifulSoup
    soup = BeautifulSoup(reqs.text, 'html.parser')
    
    # Find all 'loc' tags, which contain URLs in the sitemap
    for link in soup.findAll('loc'):
        link_text = link.text

        # Check if the URL contains any of the blacklisted substrings
        if not any(blacklisted_url in link_text for blacklisted_url in blacklisted):
            siteurls.append(link_text)

    # List of unique URLs excluding the first one
    list_urls = list(set(siteurls))

    return list_urls

## COLLECTING URLS
siteurlsraw = []

urls = []
siteurls = ['https://www.naidunia.com/world','https://www.naidunia.com/top-news','https://www.naidunia.com/rajasthan','https://www.naidunia.com/national','https://www.naidunia.com/maharashtra','https://www.naidunia.com/latest-news','https://www.naidunia.com/gujarat','https://www.naidunia.com/exam-results','https://www.naidunia.com/elections','https://www.naidunia.com/delhi-ncr','https://www.naidunia.com/chhattisgarh', 'https://www.naidunia.com/madhya-pradesh']
#output_file = '/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/Remedios/amarujala_urls.txt'

# Load existing URLs from the text file if it exists
# if os.path.exists(output_file):
#     with open(output_file, 'r') as file:
#         existing_urls = set(file.read().splitlines())
# else:
#     existing_urls = set()

section_count = 0
for section in siteurls:
    print(section)
    # open window:
    driver.get(section)
    driver.maximize_window()

    time.sleep(3)  # Allow 3 seconds for the web page to open

    for i in range(10000):
        print("Scroll Iteration: ", i)
        # Perform scroll up action
        scroll_up(driver)
        time.sleep(6) 

        if i % 10 == 0:
            # SCRAPE the website to obtain URLs
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for link in soup.findAll("a"):
                link_def = link.get("href")
                if link_def is not None:
                    parsed_url = urlparse(link_def)
                    if not parsed_url.netloc:
                        link_def2 = urljoin('https://www.naidunia.com', link_def)
                    else:
                        link_def2 = link_def
                
                urls.append(link_def2)
                    
                    # if link_def2 not in existing_urls:
                    #     existing_urls.add(link_def2)
                    #     urls.append(link_def2)
            print("URLs so far: ", len(urls))

            # # Periodically update the text file
            # with open(output_file, 'a') as file:
            #     for url in urls:
            #         file.write(url + '\n')
            # urls.clear()

            # STEP 2: Get rid or urls from blacklisted sources
            blpatterns = ['/business/', '/education/', '/entertainment/', '/horoscope-rashifal/', '/magazine/', '/special-story/', '/spiritual/', '/sports/', '/technology/', '/web-stories/', '/editorial/', '/calculator/', '/authors/', '/naidunia-rss/', '/privacy-policy/', '/contact-us/', '/cookie-policy/', '/disclaimer/', '/dnpa-code-of-ethics-for-digital-news-websites/', '/about-us/', '/advertise-withus/']
            clean_urls = []
            for url in urls:
                if "naidunia.com" in url:
                    count_patterns = 0
                    for pattern in blpatterns:
                        if pattern in url:
                            count_patterns = count_patterns + 1
                    if count_patterns == 0:
                        clean_urls.append(url)
            # List of unique urls:
            list_urls = list(set(clean_urls))

            print("Total number of USABLE urls found: ", len(list_urls))
            #time.sleep(30)

            ## INSERTING IN THE DB:
            url_count = 0
            for url in list_urls:
                if url == "":
                    pass
                else:
                    if url == None:
                        pass
                    else:
                        if "naidunia.com" in url:
                            ## SCRAPING USING NEWSPLEASE:
                            try:
                                # count:
                                url_count = url_count + 1
                                #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
                                header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                                response = requests.get(url, headers=header)
                                # process
                                article = NewsPlease.from_html(response.text, url=url).__dict__
                                # add on some extras
                                article['date_download']=datetime.now()
                                article['download_via'] = "Direct2"
                                article['source_domain'] = source


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
                                    print("+ URL: ",url)
                                    print("+ DATE: ",article['date_publish'].month)
                                    print("+ TITLE: ",article['title'][0:200])
                                    print("+ MAIN TEXT: ",article['maintext'][0:200])
                                    print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                                    pogressm = url_count/len(list_urls)
                                    print(" --> Progress:", str(pogressm), " -- Sitemamp: ", section)
                                except DuplicateKeyError:
                                    pogressm = url_count/len(list_urls)
                                    print("DUPLICATE! Not inserted. --> Progress:", str(pogressm), " -- Sitemamp: ", section)
                            except Exception as err: 
                                print("ERRORRRR......", err)
                                #pass
                        else:
                            pass


            print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db. Now waiting 63 seconds...")
            time.sleep(3)

driver.quit()

# # Ensure all collected URLs are written to the text file
# with open(output_file, 'a') as file:
#     for url in urls:
#         if url not in existing_urls:
#             file.write(url + '\n')

print("Completed URL collection")
