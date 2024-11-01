
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 18 2022

@author: diegoromero

This script updates 'themoscowtimes.com' using sitemaps.
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

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# # Set up Chrome options
chrome_options = Options()
chrome_options.binary_location = "/usr/bin/google-chrome"  # Path to Chrome binary
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--remote-debugging-port=9222")

# Initialize the WebDriver with the correct service
print("Initializing WebDriver...")
service = Service('/usr/local/bin/chromedriver')
driver = webdriver.Chrome(service=service, options=chrome_options)
print("WebDriver initialized successfully.")

# Navigate to a website
# url = "https://www.google.com"
# print(f"Navigating to {url}...")
# #driver.get(url)
# print("Navigation successful.")

# # Print the driver title
# print("Page title is:", driver.title)

# # Close the browser
# driver.quit()




# ##### Web scrapper for infinite scrolling page #####
# #driver = webdriver.Chrome('C:/Users/Yoga/OneDrive/UPenn/Works_with_Prof_Erik/ML 4Peace/chromedriver.exe')
# #driver = webdriver.Chrome()
# #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# # Set up Chrome options
# chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run in headless mode
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--window-size=1920x1080")
# chrome_options.add_argument("--disable-extensions")
# chrome_options.add_argument("--remote-debugging-port=9222")
# chrome_options.add_argument("--disable-software-rasterizer")
# chrome_options.add_argument("--disable-background-networking")
# chrome_options.add_argument("--disable-default-apps")
# chrome_options.add_argument("--disable-extensions")
# chrome_options.add_argument("--disable-sync")
# chrome_options.add_argument("--metrics-recording-only")
# chrome_options.add_argument("--safebrowsing-disable-auto-update")
# chrome_options.add_argument("--disable-web-security")

# # Initialize the WebDriver with the correct service
# print("Initializing WebDriver...")
# service = Service(ChromeDriverManager().install())
# driver = webdriver.Chrome(service=service, options=chrome_options)
# print("WebDriver initialized successfully.")


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
        time.sleep(1)
        driver.execute_script((
                "var scrollingElement = (document.scrollingElement ||"
                " document.body);scrollingElement.scrollTop ="
                " scrollingElement.scrollHeight;"))
        # Get new position
        new_position = driver.execute_script(
                ("return (window.pageYOffset !== undefined) ?"
                 " window.pageYOffset : (document.documentElement ||"
                 " document.body.parentNode || document.body);"))


# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


## COLLECTING URLS
#siteurls = ['https://fr.africanews.com/infos/', 'https://www.africanews.com/news/']
siteurls = ['https://www.africanews.com/news/']
#siteurls = ['https://fr.africanews.com/infos/']
siteurlsraw = []

#dftest = pd.DataFrame(siteurls)  
#dftest.to_csv('/Users/diegoromero/Downloads/test.csv')  

# STEP 1: Get urls of articles from sitemaps:
#for sitmp in siteurls:
#    print("Extracting from: ", sitmp)
#    reqs = requests.get(sitmp, headers=headers)
#    soup = BeautifulSoup(reqs.text, 'html.parser')
#    for link in soup.findAll('loc'):
#        urls.append(link.text)
    #for link in soup.find_all('a'):
    #    urls.append(link.get('href')) 
#    print("URLs so far: ", len(urls))

urls = []

for url in siteurls:
    print(url)
    # open window:
    driver.get(url)
    driver.maximize_window()

    # clicking on the agree and close button
    time.sleep(3)  # Allow 2 seconds for the web page to open
    print("about to click.")
    pathofbutton1 = "/html/body/div[1]/div/div/div/div/div/div[3]/button[2]"
    button = driver.find_element(By.XPATH,pathofbutton1)
    driver.execute_script("arguments[0].click();", button)
    print("just clicked")

    time.sleep(3)  # Allow 2 seconds for the web page to open

    indexp = siteurls.index(url)

    numbclicks = 0
    buttonplace = 11
    while True:
        # do whatever you want
        time.sleep(3) 
        scroll_to_bottom(driver)
        time.sleep(3)
        if numbclicks >= 100:
            break
        else:
            #soup = BeautifulSoup(driver.page_source, "html.parser")
            # clicking next:

            try: 
                # FRENCH AND ENGLISH
                if numbclicks ==0:
                    #/html/body/div[7]/main/div/div[4]/div/div[21]/div/a
                    pathofbutton = "/html/body/div[7]/main/div/div[4]/div/div[" + str(buttonplace) + "]/div/a"
                else:
                    buttonplaceupdated = buttonplace + numbclicks*10
                    pathofbutton = "/html/body/div[7]/main/div/div[4]/div/div[" + str(buttonplaceupdated) + "]/div/a"

                button = driver.find_element(By.XPATH,pathofbutton)
                driver.execute_script("arguments[0].click();", button)
                #
                numbclicks = numbclicks + 1
                print(numbclicks)

            except NoSuchElementException:
                print("Ready to obtain urls after ", numbclicks, " clicks.")
                break
            
    ### SCRAPE the website to obtain URLS
    soup = BeautifulSoup(driver.page_source, "html.parser")
    for link in soup.findAll("a"):
        urls.append(link.get("href"))
    print("URLs so far: ", len(urls))

# STEP 2: Get rid or urls from blacklisted sources
blpatterns = ['/videos/']
dedup = list(set(urls))

print("Total number of USABLE urls found: ", len(dedup))

# Manually check urls:
dftest = pd.DataFrame(dedup)  
#dftest.to_csv('C:/Users/Yoga/Dropbox/PDRI/UPenn/Works_with_Prof_Erik/ML 4Peace/Diego/africanews/africanews_news_05_2024.csv')  
print("DONE")
