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

from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.by import By

from selenium.webdriver.common.keys import Keys #need to send keystrokes

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## NEED TO DEFINE SOURCE!
source = 'manoramaonline.com'

#################
# Custom Parser #
# Custom Parser
def manoramaonline_story(soup):
    """
    Function to pull the information we want from indiatimes.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}

    # Get Title:
    try:
        #article_title = soup.find("title").text
        article_title = soup.find("div", {"class":"article-header__stamp-block"}).text
        hold_dict['title']  = article_title.replace('\u200b', '')

    except:
        article_title = None
        hold_dict['title']  = None

    # Get Main Text:
    try:
        maintext_contains = soup.find("div", {"class":"rtearticle text"}).text
        hold_dict['maintext'] = maintext_contains.replace('\u200b', '')
    except:
        maintext = None
        hold_dict['maintext']  = None


    # Get Date:
    try:
        date_contains = soup.find("span", {"class":"story-publish-date"}).text.replace('Published: ', '')
        date = dateparser.parse(date_contains, date_formats=['%d/%m/%Y'])
        hold_dict['date_publish'] = date
    except:
        hold_dict['date_publish'] = None

    return hold_dict
##
#################

sections = ['/news/latest-news.html', '/news/world.html', '/news/india.html', '/news/kerala.html', '/news/editorial.html', '/news/sunday.html', '/tagresults.html?tag=mo%3Acrime%2Fcrime-news', '/global-malayali/gulf.html', '/global-malayali/europe.html', '/global-malayali/us.html', '/global-malayali/other-countries.html', '/global-malayali/my-creatives.html',
            '/district-news/thiruvananthapuram.html', '/district-news/kollam.html', '/district-news/pathanamthitta.html', '/district-news/alappuzha.html', '/district-news/kottayam.html', '/district-news/idukki.html', '/district-news/idukki.html', '/district-news/ernakulam.html',
            '/district-news/thrissur.html', '/district-news/palakkad.html', '/district-news/kozhikode.html', '/district-news/malappuram.html', '/district-news/wayanad.html', '/district-news/kannur.html', '/district-news/kasargod.html', '/district-news/chennai.html', '/district-news/bengaluru.html',
            '/district-news/mumbai.html', '/district-news/new-delhi.html', '/district-news/kerala-lottery-results.html', '/district-news/chuttuvattom-award.html']
positions = [100, 11, 43, 100, 58, 10, 1000, 101, 82, 101, 12, 8, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 286, 283, 279, 277, 5, 1]

for i in range(len(sections)):
    section_name = sections[i]
    page_num = positions[i]

  #print(section_page)
    for page in range(1, 15 +1):

        if page ==1:
            section_page = 'https://www.manoramaonline.com/' + section_name
        else:
            #page = (page - 1) * 20
            section_page = 'https://www.manoramaonline.com/' + section_name + "?page=" + str(page)
        print(section_page)

        reqs = requests.get(section_page, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')
        #print(soup.find('div', {'id':'tdi_54'}))

        urls = []
        try:
            for link in soup.find('div', {'class':'story-col-list-section'}).find_all('a'):
                link1 = 'https://www.manoramaonline.com' + link.get('href')
                print(link1)
                #print(link)
                urls.append(link1)
                urls = list(set(urls))
                print("URLs so far: ",len(urls))
        except:
            pass

        print(urls)
        ## INSERTING IN THE DB:
        url_count = 0
        for url in urls:
            if url == "":
                pass
            else:
                if url == None:
                    pass
                else:
                    if "manoramaonline.com" in url:
                        print(url, "FINE")
                        ## SCRAPING USING NEWSPLEASE:
                        try:
                            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
                            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                            response = requests.get(url, headers=header)
                            soup = BeautifulSoup(response.text, 'html.parser')

                            # process
                            article = NewsPlease.from_html(response.text, url=url).__dict__
                            # add on some extras
                            article['date_download']=datetime.now()
                            article['download_via'] = "Direct2"
                            article['title'] = manoramaonline_story(soup)['title']
                            article['date_publish'] = manoramaonline_story(soup)['date_publish']
                            article['maintext'] = manoramaonline_story(soup)['maintext']

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
                                print(article['date_publish'])
                                #print(article['date_publish'].month)
                                print(article['title'][0:100])
                                print(article['maintext'][0:100])
                                db['urls'].insert_one({'url': article['url']})
                                print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                            except DuplicateKeyError:
                                print("DUPLICATE! Not inserted.")
                        except Exception as err:
                            print("ERRORRRR......", err)
                            pass
                    else:
                        pass


        #print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")

