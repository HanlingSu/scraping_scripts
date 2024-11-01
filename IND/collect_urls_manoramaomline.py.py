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

from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.by import By

from selenium.webdriver.common.keys import Keys #need to send keystrokes

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import datetime as dt
import pandas as pd


#### selenium headless
from selenium.webdriver.chrome.options import Options
chrome_options = Options()

chrome_options.add_argument("--headless")
chrome_options.headless = True # also works
driver = webdriver.Chrome(options=chrome_options)
######
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
######

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

chrome_driver_path = "C:/Program Files/driver/chromedriver_win32/chromedriver.exe"  # Path to your Chrome WebDriver executabl
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode, without opening a window
driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)


urls = []
for section in sections:
                
    archiveurl = "https://www.manoramaonline.com/" + section + ".html"

    # Starting:
    driver.get(archiveurl)
    driver.maximize_window()
    time.sleep(2)  # Allow 2 seconds for the web page to open
    scroll_to_bottom(driver)
    time.sleep(3)  # Allow 2 seconds for the web page to load
    scroll_pause_time = 2 # You can set your own pause time.
    screen_height = driver.execute_script("return window.screen.height;")   # get the screen height of the web
    i = 1

    while True:
        # scroll one screen height each time
        driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))  
        i += 1
        print(i)
        time.sleep(scroll_pause_time)
        # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
        scroll_height = driver.execute_script("return document.body.scrollHeight;")  

        # Break the loop when the height we need to scroll to is larger than the total scroll height
        if (screen_height) * i > scroll_height:
            if i < 5:
                scroll_to_bottom(driver)
                time.sleep(3) 
            else:
                break
        else:
            break

    ### SCRAPE the website to obtain URLS
    soup = BeautifulSoup(driver.page_source, "html.parser")
    for link in soup.findAll("a"):
        urls.append(link.get("href"))
    print("URLs so far: ", len(urls))
    

# URLS for the month:
#csvstring = "C:/Users/Yoga/OneDrive/UPenn/Works_with_Prof_Erik/ML 4Peace/Diego/manoramaonline.csv"
#dfurls = pd.DataFrame(urls)  
#dfurls.to_csv(csvstring, index = False)  
#print("Done with ", len(dfurls), " from ", section)

#print("....................... DONE .......................")
