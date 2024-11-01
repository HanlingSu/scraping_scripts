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
siteurls = ['https://www.amarujala.com/india-news?src=mainmenu']
output_file = '/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/Remedios/amarujala_urls.txt'

# Load existing URLs from the text file if it exists
if os.path.exists(output_file):
    with open(output_file, 'r') as file:
        existing_urls = set(file.read().splitlines())
else:
    existing_urls = set()

section_count = 0
for section in siteurls:
    print(section)
    # open window:
    driver.get(section)
    driver.maximize_window()

    time.sleep(3)  # Allow 3 seconds for the web page to open

    for i in range(100000):
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
                        link_def2 = urljoin('https://www.amarujala.com', link_def)
                    else:
                        link_def2 = link_def
                    if link_def2 not in existing_urls:
                        existing_urls.add(link_def2)
                        urls.append(link_def2)
            print("URLs so far: ", len(existing_urls))

            # Periodically update the text file
            with open(output_file, 'a') as file:
                for url in urls:
                    file.write(url + '\n')
            urls.clear()

driver.quit()

# Ensure all collected URLs are written to the text file
with open(output_file, 'a') as file:
    for url in urls:
        if url not in existing_urls:
            file.write(url + '\n')

print("Completed URL collection")
