#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 1 2024

@author: Togbedji

This script updates 'navarashtra.com' using sitemaps.
It can be run as often as one desires. 
 
"""


# Packages:
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
from bs4 import BeautifulSoup
# %pip install dateparser
import dateparser
import pandas as pd
from newsplease import NewsPlease

import time
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urlparse

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.by import By

from selenium.webdriver.common.keys import Keys #need to send keystrokes

source = "navarashtra.com"
##### Web scrapper for infinite scrolling page #####
#driver = webdriver.Chrome('C:/Users/Yoga/OneDrive/UPenn/Works_with_Prof_Erik/ML 4Peace/chromedriver.exe')
#driver = webdriver.Chrome()
#driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

driver = webdriver.Chrome(ChromeDriverManager().install())
#driver.get("http://www.python.org")

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

    # Calculate new scroll position to scroll up a little bit (e.g., 500 pixels)
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
siteurls = ['https://www.navarashtra.com/maharashtra/', 'https://www.navarashtra.com/india/', 'https://www.navarashtra.com/world/', 'https://www.navarashtra.com/viral/', 'https://www.navarashtra.com/crime/', 'https://www.navarashtra.com/business/', 'https://www.navarashtra.com/technology/', 'https://www.navarashtra.com/education/']
section_count = 0
for section in siteurls:
    print(section)
    # open window:
    driver.get(section)
    driver.maximize_window()

    time.sleep(3)  # Allow 2 seconds for the web page to open

    for i in range(100):
        print(i)
        # do whatever you want
        #scroll_to_bottom(driver)
        #time.sleep(3) 
        scroll_up(driver)
        time.sleep(6) 

        if i % 10 == 0:
        ### SCRAPE the website to obtain URLS
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for link in soup.findAll("a"):
                link_def = link.get("href")
                if link_def != None:
                    #link_def2 = 'navarashtra.com' + link_def
                    urls.append(link_def)
            print("URLs so far: ", len(urls))

            dedup = list(set(urls))

            # # Manually check urls:
            # dftest = pd.DataFrame(dedup)  
            # filename = 'C:/Users/Yoga/Dropbox/PDRI/UPenn/Works_with_Prof_Erik/ML 4Peace/Diego/navarashtra/navarashtra_' + str(i) + '.csv'
            # dftest.to_csv(filename) 
