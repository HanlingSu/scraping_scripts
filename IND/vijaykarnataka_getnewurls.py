#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on April 11 2023

@author: bhumika

This script updates vijaykarnataka.com
 
"""

# Packages:
import random
import sys
sys.path.append('../')
import os
import re
# from p_tqdm import p_umap
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
# from dotenv import load_dotenv
from bs4 import BeautifulSoup
# %pip install dateparser
import dateparser
import pandas as pd

import math


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## NEED TO DEFINE SOURCE!
source = 'vijaykarnataka.com'

def vijaykarnataka_story(soup):
    hold_dict = {}
    # Get Title: 
    try:
        article_titlec = soup.find("meta", {"property":"og:title"})
        article_title = article_titlec["content"]
        hold_dict['title']  = article_title   
    except:
        try:
            article_title = soup.find("title").text
            hold_dict['title']  = article_title 
        except:
            hold_dict['title']  = None
        
    # Get Main Text:
    hold_dict['maintext'] = None
    try:
        a = soup.find("div", attrs={'class': "full_article"})
        text = a.text
        hold_dict['maintext'] = text
    except:
        try: 
            hold_dict['maintext'] = soup.find("div", attrs={"itemprop":"description"}).text
        except:   
            hold_dict['maintext'] = None

    # Get Date
    try:
        containsdate = soup.find("span",{"class":"time"})
        date_text = re.sub(r'<[^>]+?>', '', containsdate.text)
        article_date = datetime.strptime(date_text, "%d %b %Y, %I:%M %p")
        hold_dict['date_publish'] = article_date
        
    except Exception as err:
        hold_dict['date_publish'] = None
        print("Error when trying to get the date", err)

    return hold_dict


def sitemap_to_url(sitemap, headers):
    req = requests.get(sitemap, headers = headers)
    soup = BeautifulSoup(req.content)
    sitemap_URLs = []
    blcklist = ["/tv", "/cinema", "/astrology", "/namma-baza", "/lifestyle", "/entertainment"]
    for i in soup.find_all('loc'):
        if not any([x in i.text for x in blcklist]):
            sitemap_URLs.append(i.text)
    print('Now collected',len(sitemap_URLs), 'sitemap URLs')
    return sitemap_URLs

def sitemap_to_sitemap(sitemap, headers):
    req = requests.get(sitemap, headers = headers)
    soup = BeautifulSoup(req.content)
    sitemap_to_sitemap_URLs = []
    blcklist = ["/tv", "/cinema", "/astrology", "/namma-baza", "/lifestyle", "/entertainment"]
    for i in soup.find_all('loc'):
        if not any([x in i.text for x in blcklist]):
            sitemap_to_sitemap_URLs.append(i.text)
    print('Now collected',len(sitemap_to_sitemap_URLs), 'sitemap URLs in sitemap')
    return sitemap_to_sitemap_URLs

def sitemap_to_section(sitemap, headers):
    req = requests.get(sitemap, headers = headers)
    soup = BeautifulSoup(req.content)
    sitemap_to_section_URLs = []
    blcklist = ["/tv", "/cinema", "/astrology", "/namma-baza", "/lifestyle", "/entertainment"]
    for i in soup.find_all('loc'):
        if not any([x in i.text for x in blcklist]):
            sitemap_to_section_URLs.append(i.text)
    print('Now collected',len(sitemap_to_section_URLs), 'section URLs in sitemap')
    return sitemap_to_section_URLs

def clean_url(sitemap_URLs) :
    blpatterns = ["/tv", "/cinema", "/astrology", "/namma-baza", "/lifestyle", "/entertainment"]

    clean_urls = set()
    for url in sitemap_URLs:
        if url == "" or url == None:
            continue

        for pattern in blpatterns:
            if pattern in url:
                break
        else:
            if not "https://www.vijaykarnataka.com/" in url and not "https:" in url:
                url = "https://www.vijaykarnataka.com/" + url
            clean_urls.add(url)
    print('Now collected ',len(clean_urls), ' clean inner URLs')
    return clean_urls

def section_to_url(section, headers):
    section_inner_urls = set()
    end_limit = 100
    blpatterns = ["/tv", "/cinema", "/astrology", "/namma-baza", "/lifestyle", "/entertainment"]
    for pattern in blpatterns:
        if pattern in section:
            return section_inner_urls
    print("section", section)

    if section == "https://vijaykarnataka.com":
      end_limit = 2
    for j in range(1,end_limit):
        url_to_parse = section + "?curpg=" + str(j)
        req = requests.get(url_to_parse, headers = headers)
        soup = BeautifulSoup(req.content, 'html.parser')
        print("****j ", j)
        try : 
            if soup.find("img", attrs={"title":"404 Error Found"}):
                break
            for link in soup.find_all('a'):
              section_inner_urls.add(link.get('href')) 
        except Exception as err:
            print('Exception found while getting the url from section: ', section)

    print('Now collected ',len(section_inner_urls), 'section inner URLs for last j: ', j)
    return section_inner_urls

def extract_url_information(clean_urls):
    url_count = 0
    final_section_incorrect_data = []
    final_section_data = []
    for section_clean_url in clean_urls:
        ## SCRAPING USING NEWSPLEASE:
        try:
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            response = requests.get(section_clean_url, headers=header)

            # process
            article = NewsPlease.from_html(response.text, url=section_clean_url).__dict__
            article['date_download'] = datetime.now()
            article['download_via'] = "LocalIND"
            article['source_domain'] = source

            soup = BeautifulSoup(response.content, 'html.parser')

            extracted_data = vijaykarnataka_story(soup)

            article['date_publish'] = extracted_data['date_publish']
            article['title'] = extracted_data['title']
            article['maintext'] = extracted_data['maintext']
            final_section_data.append(article)
            
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'articles-{year}-{month}'
            except:
                print("NO DATE : ", section_clean_url)
                colname = 'articles-nodate'
            try:
                url_count = url_count + 1
                # print(article)
                # Inserting article into the db:
                db[colname].insert_one(article)
                # print(" + Date: ", article['date_publish'], " + Main Text: ", article['maintext'][0:50], " + Title: ", article['title'][0:25])
                # print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                db['urls'].insert_one({'url': article['url']})
            except DuplicateKeyError:
                print("DUPLICATE! Not inserted for section clean url : ", section_clean_url)

        except Exception as err:
            print("Exception in section clean url : ", section_clean_url)
            final_section_incorrect_data.append({'url': section_clean_url, "err": err})
            print("ERRORRRR......", err)
    return final_section_incorrect_data, final_section_data


sitemap = "https://vijaykarnataka.com/staticsitemap/vk/sitemap-index.xml"
sitemap_to_sitemap_URLs =['https://vijaykarnataka.com/staticsitemap/vk/2024-April.xml', 'https://vijaykarnataka.com/staticsitemap/vk/2024-March.xml', 'https://vijaykarnataka.com/staticsitemap/vk/2024-February.xml', 'https://vijaykarnataka.com/staticsitemap/vk/2024-January.xml', 'https://vijaykarnataka.com/staticsitemap/vk/2023-December.xml', 'https://vijaykarnataka.com/staticsitemap/vk/2023-November.xml', 'https://vijaykarnataka.com/staticsitemap/vk/2023-October.xml', 'https://vijaykarnataka.com/staticsitemap/vk/2023-September.xml', 'https://vijaykarnataka.com/staticsitemap/vk/2023-August.xml', 'https://vijaykarnataka.com/staticsitemap/vk/2023-July.xml', 'https://vijaykarnataka.com/staticsitemap/vk/2023-June.xml', 'https://vijaykarnataka.com/staticsitemap/vk/2023-May.xml', 'https://vijaykarnataka.com/staticsitemap/vk/2023-April.xml', 'https://vijaykarnataka.com/staticsitemap/vk/2023-March.xml'] #sitemap_to_sitemap(sitemap, headers)
# count = 0
sitemap_URLs = []
for sitemap in sitemap_to_sitemap_URLs:  
    sitemap_URLs.extend(sitemap_to_url(sitemap, headers))
    # count += 1
    # if count > 0:
    #   break
clean_urls = clean_url(sitemap_URLs)
final_section_incorrect_data, final_section_data = extract_url_information(clean_urls)
print("Found " + str(len(final_section_data)) + " articles from sitemap :" + sitemap)


sitemaps = ["https://vijaykarnataka.com/sitemap/yesterday",
            "https://vijaykarnataka.com/sitemap/today"]
for sitemap in sitemaps:
    sitemap_URLs = []
    sitemap_URLs.extend(sitemap_to_url(sitemap, headers))
    clean_urls = clean_url(sitemap_URLs)
    final_section_incorrect_data, final_section_data = extract_url_information(clean_urls)
    print("Found " + str(len(final_section_data)) + " articles from sitemap :" + sitemap)


sitemap = "https://vijaykarnataka.com/sitemapxml.cms"
sitemap_URLs = []
sitemap_URLs.extend(sitemap_to_section(sitemap, headers))
# coutn = 0
for url in sitemap_URLs:
    sec_url = []
    sec_url.extend(section_to_url(url, headers))
    clean_urls = clean_url(sec_url)
    final_section_incorrect_data, final_section_data = extract_url_information(clean_urls)
    print("Found " + str(len(final_section_data)) + " articles from sitemap :" + sitemap)