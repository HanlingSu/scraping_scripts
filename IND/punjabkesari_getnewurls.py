#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on March 6 2023

@author: bhumika

This script updates punjabkesari.in 
 
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
source = 'punjabkesari.in'


def punjabkesari_story(soup):

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
        hold_dict['maintext'] = soup.find("div", attrs={'class': "descriptionC"}).text
    except:
        hold_dict['maintext'] = None

    # Get Date
    try:
        uploadtime_tag = soup.find('p', itemprop='uploadtime')

        # Extract the text content within the <p> tag
        uploadtime_text = uploadtime_tag.get_text()
        parts = uploadtime_text.split()

        # Extract date and time separately
        date_part = ' '.join(parts[2:5])

        # Convert the date and time strings to datetime objects
        date =  datetime.strptime(date_part, '%b %d, %Y')
        hold_dict['date_publish'] = date
    except Exception as err:
        hold_dict['date_publish'] = None
        print("Error when trying to get the date", err)

    return hold_dict

def url_to_subsection_url(url, header):
    response = requests.get(url, headers=header)
    soup = BeautifulSoup(response.content, 'html.parser')

    links = soup.findAll("a", attrs={'class': 'dropdown-item'})

    links_to_query = []
    for l in links: 
        links_to_query.append(l.attrs["href"])
    print("Found ", (len(links_to_query)) , " sections in the main site")

    return links_to_query

def sitemap_to_url(sitemap, headers):
    req = requests.get(sitemap, headers = headers)
    soup = BeautifulSoup(req.content)
    sitemap_URLs = []
    for i in soup.find_all('loc'):
        sitemap_URLs.append(i.text)
    print('Now collected',len(sitemap_URLs), 'sitemap URLs')
    return sitemap_URLs

def sitemap_to_section(sitemap, headers):
    req = requests.get(sitemap, headers = headers)
    soup = BeautifulSoup(req.content)
    sitemap_to_section_URLs = []
    for i in soup.find_all('loc'):
        sitemap_to_section_URLs.append(i.text)
    print('Now collected',len(sitemap_to_section_URLs), 'section URLs in sitemap')
    return sitemap_to_section_URLs

def clean_url(sitemap_URLs) :
    blpatterns = ['/dharm', "/sports"]
    clean_urls = set()
    for url in sitemap_URLs:
        if url == "" or url == None:
            continue

        for pattern in blpatterns:
            if pattern in url:
                break
        else:
            if not "https://www.punjabkesari.in/" in url and not "https:" in url:
                url = "https://www.punjabkesari.in/" + url
            clean_urls.add(url)
    print('Now collected ',len(clean_urls), ' clean inner URLs')
    return clean_urls

def section_to_url(section, headers):
    section_inner_urls = set()
    c = section.split(".punjabkesari.in")
    if c[0] != "https://www":
        section = section + "/" + c[0].replace("https://", "")
    for j in range(1,51):
        url_to_parse = section + "/page/" + str(j)
        req = requests.get(url_to_parse, headers = headers)
        soup = BeautifulSoup(req.content, 'html.parser')
        #https://www.punjabkesari.in/delhi/new-delhi/page/15 >>> NOT FOUND
        for link in soup.find_all('a'):
            section_inner_urls.add(link.get('href')) 
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

            extracted_data = punjabkesari_story(soup)

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


subsections = url_to_subsection_url("https://www.punjabkesari.in", headers)
sections = sitemap_to_section("https://www.punjabkesari.in/category.xml", headers)
super_section = set()
super_section |= set(sections)
super_section |= set(subsections)
for section in list(super_section): 
    section_URLs = section_to_url(section, headers)
    clean_urls = clean_url(section_URLs)
    final_section_incorrect_data, final_section_data = extract_url_information(clean_urls)
    print("Found " + str(len(final_section_data)) + " articles from section :" + section)



sitemaps = ['https://www.punjabkesari.in/newssitemap.xml' , 'https://www.punjabkesari.in/sitemap-national.xml'	, 
            'https://www.punjabkesari.in/sitemap-international.xml'	, 'https://www.punjabkesari.in/sitemap-business.xml'] 
for sitemap in sitemaps :
    sitemap_URLs = sitemap_to_url(sitemap, headers)
    clean_urls = clean_url(sitemap_URLs)
    final_section_incorrect_data, final_section_data = extract_url_information(clean_urls)
    print("Found " + str(len(final_section_data)) + " articles from sitemap :" + sitemap)