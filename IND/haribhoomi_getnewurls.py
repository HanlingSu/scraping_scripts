#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on March 10 2023

@author: bhumika & Togbedji

This script updates haribhoomi.com
 
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
source = 'haribhoomi.com'


# def haribhoomi_story(soup):
#     hold_dict = {}

#     # Get Title: 
#     try:
#         article_titlec = soup.find("meta", {"property":"og:title"})
#         article_title = article_titlec["content"]
#         hold_dict['title']  = article_title.replace("| Hari Bhoomi", "")
#     except:
#         try:
#             article_title = soup.find("title").text
#             hold_dict['title']  = article_title.replace("| Hari Bhoomi", "") 
#         except:
#             hold_dict['title']  = None
        
#     # Get Main Text:
#     hold_dict['maintext'] = None
#     try:
#         hold_dict['maintext']  = soup.find("div", attrs={'class': 'story_content'}).text
#     except:
#         hold_dict['maintext'] = None

#     # Get Date
#     try:
#         containsdate = soup.find("span",{"class":"convert-to-localtime"}).text
#         a = containsdate.split(" ")
#         if len(a[1]) > 3:
#             article_date = datetime.strptime(a[0] + " " + a[1] + " " +a[2], "%d %B %Y")
#         else: 
#             article_date = datetime.strptime(a[0] + " " + a[1] + " " +a[2], "%d %b %Y")
#         hold_dict['date_publish'] = article_date
#     except Exception as err:
#         hold_dict['date_publish'] = None
#         print("Error when trying to get the date", err)

#     return hold_dict

# def sitemap_to_modified_url(sitemap, headers):
#     req = requests.get(sitemap, headers = headers)
#     soup = BeautifulSoup(req.content)
#     sitemap_URLs = []
#     for i in soup.find_all('loc'):
#         sitemap_URLs.append(i.text.split(" ")[1])
#     print('Now collected',len(sitemap_URLs), 'sitemap URLs')
#     return sitemap_URLs

# def sitemap_to_modified_url_link(sitemap, headers):
#     req = requests.get(sitemap, headers = headers)
#     soup = BeautifulSoup(req.content)
#     sitemap_URLs = []
#     for i in soup.find_all('link'):
#         sitemap_URLs.append(i.text)
#     print('Now collected',len(sitemap_URLs), 'sitemap URLs')
#     return sitemap_URLs

# def sitemap_to_url(sitemap, headers):
#     req = requests.get(sitemap, headers = headers)
#     soup = BeautifulSoup(req.content)
#     sitemap_URLs = []
#     for i in soup.find_all('loc'):
#         sitemap_URLs.append(i.text)
#     print('Now collected',len(sitemap_URLs), 'sitemap URLs')
#     return sitemap_URLs

# def sitemap_to_sitemap(sitemap, headers):
#     req = requests.get(sitemap, headers = headers)
#     soup = BeautifulSoup(req.content)
#     sitemap_to_sitemap_URLs = []
#     for i in soup.find_all('loc'): 
#         if ("photo-story-sitemap.xml" not in i.text) and ("authors-sitemap.xml" not in i.text):
#             sitemap_to_sitemap_URLs.append(i.text)
#     print('Now collected',len(sitemap_to_sitemap_URLs), 'sitemap URLs in sitemap')
#     return sitemap_to_sitemap_URLs

# def sitemap_to_section(sitemap, headers):
#     req = requests.get(sitemap, headers = headers)
#     soup = BeautifulSoup(req.content)
#     sitemap_to_section_URLs = []
#     blpatterns = ['/tech-and-auto/', '/webstories/', '/rashifal/', '/religion/', 
#               '/sports/', '/entertainment', '/lifestyle/', '/photo-gallery',
#               '/automobiles-and-gadget', '/jokes', '/astrology-and-spirituality'
#               ]
#     for i in soup.find_all('loc'):
#         if not any([x in i.text for x in blpatterns]):
#             sitemap_to_section_URLs.append(i.text)
#     print('Now collected',len(sitemap_to_section_URLs), 'section URLs in sitemap')
#     return sitemap_to_section_URLs


# def clean_url(sitemap_URLs) :
#     blpatterns = ['/tech-and-auto/', '/webstories/', '/rashifal/', '/religion/', 
#                   '/sports/', '/entertainment', '/lifestyle/', '/photo-gallery',
#                   '/automobiles-and-gadget', '/jokes', '/astrology-and-spirituality'
#                   ]
#     clean_urls = set()
#     for url in sitemap_URLs:
#         if url == "" or url == None:
#             continue

#         for pattern in blpatterns:
#             if pattern in url:
#                 break
#         else:
#             if not "https://www.haribhoomi.com/" in url and not "https:" in url:
#                 url = "https://www.haribhoomi.com" + url
#             clean_urls.add(url)
#     print('Now collected ',len(clean_urls), ' clean inner URLs')
#     return clean_urls

# def section_to_url(section, headers):
#     section_inner_urls = set()
#     req = requests.get(section, headers = headers)
#     soup = BeautifulSoup(req.content, 'html.parser')

#     if soup.find('p',{"class":"no-data-found"}):
#         return section_inner_urls
#     for link in soup.find_all('a'):
#         section_inner_urls.add(link.get('href'))

#     for j in range(1,66300):
#         url_to_parse = section + "/" + str(j)
#         req = requests.get(url_to_parse, headers = headers)
#         soup = BeautifulSoup(req.content, 'html.parser')

#         if soup.find('p',{"class":"no-data-found"}):
#             break
#         for link in soup.find_all('a'):
#             section_inner_urls.add(link.get('href')) 
#     print('Now collected ',len(section_inner_urls), 'section inner URLs for last j: ', j , 'section :', section)
#     return section_inner_urls

# def extract_url_information(clean_urls):
#     url_count = 0
#     final_section_incorrect_data = []
#     final_section_data = []
#     for section_clean_url in clean_urls:
#         ## SCRAPING USING NEWSPLEASE:
#         try:
#             header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
#             response = requests.get(section_clean_url, headers=header)

#             # process
#             article = NewsPlease.from_html(response.text, url=section_clean_url).__dict__
#             article['date_download'] = datetime.now()
#             article['download_via'] = "LocalIND"
#             article['source_domain'] = source

#             soup = BeautifulSoup(response.content, 'html.parser')

#             extracted_data = haribhoomi_story(soup)

#             article['date_publish'] = extracted_data['date_publish']
#             article['title'] = extracted_data['title']
#             article['maintext'] = extracted_data['maintext']
#             final_section_data.append(article)
            
#             try:
#                 year = article['date_publish'].year
#                 month = article['date_publish'].month
#                 colname = f'articles-{year}-{month}'
#             except:
#                 print("NO DATE : ", section_clean_url)
#                 colname = 'articles-nodate'
#             try:
#                 url_count = url_count + 1
#                 # print(article)
#                 # Inserting article into the db:
#                 db[colname].insert_one(article)
#                 # print(" + Date: ", article['date_publish'], " + Main Text: ", article['maintext'][0:50], " + Title: ", article['title'][0:25])
#                 # print("Inserted! in ", colname, " - number of urls so far: ", url_count)
#                 db['urls'].insert_one({'url': article['url']})
#             except DuplicateKeyError:
#                 print("DUPLICATE! Not inserted for section clean url : ", section_clean_url)

#         except Exception as err:
#             print("Exception in section clean url : ", section_clean_url)
#             final_section_incorrect_data.append({'url': section_clean_url, "err": err})
#             print("ERRORRRR......", err)
#     return final_section_incorrect_data, final_section_data

# # sitemap = "https://www.haribhoomi.com/news-sitemap-daily.xml"
# # sitemap_URLs = sitemap_to_url(sitemap, headers)
# # clean_urls = clean_url(sitemap_URLs)
# # final_section_incorrect_data, final_section_data = extract_url_information(clean_urls)
# # print("Found " + str(len(final_section_data)) + " articles from sitemap :" + sitemap)

# sitemap = "https://www.haribhoomi.com/sitemap/sitemap-index.xml"
# sitemap_to_sitemap_URLs = sitemap_to_sitemap(sitemap, headers)
# count = 0
# sitemap_URLs = []
# for sitemap in sitemap_to_sitemap_URLs:
#     if sitemap == "https://www.haribhoomi.com/sitemap/sitemap-home.xml":
#         section_URLs = sitemap_to_section(sitemap, headers)
#         for section in section_URLs:
#             sitemap_URLs = []
#             sitemap_URLs.extend(list(section_to_url(section, headers)))
#             clean_urls = clean_url(sitemap_URLs)
#             final_section_incorrect_data, final_section_data = extract_url_information(clean_urls)
#             print("Found " + str(len(final_section_data)) + " articles from sitemap :" + sitemap, " section : ", section)
#     elif "sitemap/news-" in sitemap:
#         sitemap_URLs = []
#         sitemap_URLs.extend(list(sitemap_to_modified_url(sitemap, headers)))
#         clean_urls = clean_url(sitemap_URLs)
#         final_section_incorrect_data, final_section_data = extract_url_information(clean_urls)
#         print("Found " + str(len(final_section_data)) + " articles from sitemap :" + sitemap)


# sitemap = "https://www.haribhoomi.com/feeds.xml"
# sitemap_URLS =  sitemap_to_modified_url_link(sitemap, headers)
# count = 0
# for url in sitemap_URLS:
#     clean_urls = clean_url(url)
#     final_section_incorrect_data, final_section_data = extract_url_information(clean_urls)
#     print("Found " + str(len(final_section_data)) + " articles from sitemap :" + url)


#################
# Custom Parser #
# Custom Parser
def haribhoomi_story(soup):
    """
    Function to pull the information we want from indiatimes.com stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}

    # Get Title:
    try:
        #article_title = soup.find("title").text
        article_title = soup.find("div", {"class":"featured-heading-block"}).text
        hold_dict['title']  = article_title.replace('\u200b', '')

    except:
        article_title = None
        hold_dict['title']  = None

    # Get Main Text:
    try:
        maintext_contains1 = soup.find("div", {"class":"summary"}).text
        maintext_contains2 = soup.find("div", {"class":"story-content"}).text
        hold_dict['maintext'] = maintext_contains1 + maintext_contains2
    except:
        maintext = None
        hold_dict['maintext']  = None


    # Get Date:
    try:
        date_contains = soup.find("div", {"class":"article-meta"}).find('li').text
        date_mod = date_contains.replace('Published: ', '')
        date = dateparser.parse(date_mod, date_formats=['%d/%m/%Y'])
        hold_dict['date_publish'] = date
    except:
        hold_dict['date_publish'] = None

    return hold_dict
##
#################


sections = ['/topic/lok-sabha-election-2024', '/state-local','/hb-exclusive/news', '/topic/ipl-2024', '/trending/news', '/national/news', '/world/news', '/opinion/news']
positions = [1, 151, 3, 1, 3, 1, 8, 1]


for i in range(len(sections)):
    
    section_name = sections[i]
    page_num = positions[i]

    print(section_name)
    for page in range(1, page_num +1):
        
        if page ==1:
            section_page = 'https://www.haribhoomi.com/' + section_name
        else:
            page = (page - 1) * 20
            section_page = 'https://www.haribhoomi.com/' + section_name + "/news/" + str(page)
        #print(section_page)

        reqs = requests.get(section_page, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')
        #print(soup.find('div', {'id':'tdi_54'}))
        
        urls = []
        try:
            for link in soup.find('div', {'class':'listing-news-ok'}).find_all('a'):
                link1 = link.get('href')

                if 'www.haribhoomi.com' in link1:
                    print(link1)
                    urls.append(link1)
                    urls = list(set(urls))
                else:
                    link1 = 'https://www.haribhoomi.com' + link.get('href')
                    print(link1)
                    urls.append(link1)
                    urls = list(set(urls))
        except:
            pass
    
        print("URLs so far: ",len(urls))

        ## INSERTING IN THE DB:
        url_count = 0
        for url in urls:
            if url == "":
                pass
            else:
                if url == None:
                    pass
                else:
                    if "haribhoomi.com" in url:
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
                            article['title'] = haribhoomi_story(soup)['title']
                            article['date_publish'] = haribhoomi_story(soup)['date_publish']
                            article['maintext'] = haribhoomi_story(soup)['maintext']

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
                                print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                                db['urls'].insert_one({'url': article['url']})
                            except DuplicateKeyError:
                                print("DUPLICATE! Not inserted.")
                        except Exception as err:
                            print("ERRORRRR......", err)
                            pass
                    else:
                        pass


        print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")

