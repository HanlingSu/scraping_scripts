"""
Created on July 22 2022

@author: serkantadiguzel

This script scrapes/updates 'hvg.hu' using sitemaps. 

There is no sitemap, so we need to loop through different sections on the web page. I identified three important sections that need to be scraped. Please update three parts below (noted as #Change) and scrape the first couple of pages depending on when we will update next time.
""" 
 
import random
import sys
import os
import re
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from pymongo.errors import CursorNotFound
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date, timedelta
from newsplease import NewsPlease
from datetime import datetime
import dateparser
import time
import cloudscraper


scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)


hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}



# db connection: THIS LINE WILL CHANGE ONCE WE HAVE A NEW DB WORKING AT PENN
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p



#econ: https://hvg.hu/gazdasag/6288?ver=1 till 6290.
#local: https://hvg.hu/itthon/9000?ver=1 till 10601.
#world: https://hvg.hu/vilag/6?ver=1 till 6531.



headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

source = 'hvg.hu'






# Custom Parser
def hvg_story(soup):
    """
    Function to pull the information we want from hvg.hu stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    # get title
    try:
        title = soup.find('div', {'class' : 'article-title article-title'}).text.strip()
    except:
        title = None

    hold_dict['title'] = title
        
    # Get Highlighted Text:
    try:
        highlighted_text = soup.find('div', {'class': 'article-lead entry-summary'}).text.strip()
        if highlighted_text == '':
            highlighted_text = None         
    except:
        highlighted_text = None

    # Get Main Text:
    try:
        contains_maintext = soup.find("div", {"class":"article-content entry-content"})
        maintext = contains_maintext.text.strip()
        
    except: 
        maintext = None

    try:
        combined_text = highlighted_text + ' '+ maintext
        hold_dict['maintext'] = combined_text  
    except:
        combined_text = maintext
        hold_dict['maintext'] = combined_text

   
    return hold_dict





## econ news first
baseurl1 = 'https://hvg.hu/gazdasag/'
links = []
for i in range(1, 60): ##CHANGE: There were 6481 pages when scraped. So the first x - 6481 pages need to be scraped next time. 
    linkpageURL = baseurl1 + str(i) + '?ver=1'
    print(linkpageURL)
    #reqs = requests.get(linkpageURL, headers=headers)
    reqs = scraper.get(linkpageURL)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    for h2 in soup.find_all('h2', {'class' : 'heading-3'}):
        a = h2.find('a', href=True)
        final_link = 'https://hvg.hu' + a['href']
        links.append(final_link)
    print(len(links))

clean_links1 = list(set(links))





## INSERTING IN THE DB:
url_count = 0
for url in clean_links1:
    if url == "":
        continue
    else:
        if url == None:
            continue
    
    try:
        #response = requests.get(url, headers=headers)
        response = scraper.get(url)
        #article = NewsPlease.from_url(url).__dict__
        article = NewsPlease.from_html(scraper.get(url).text).__dict__
    except:
        time.sleep(0.5)
        try:
            #response = requests.get(url, headers=headers)
            response = scraper.get(url)
            article = NewsPlease.from_html(scraper.get(url).text).__dict__

            #article = NewsPlease.from_url(url).__dict__
        except:
            continue


    soup = BeautifulSoup(response.text, 'html.parser')
       
    # add on some extras
    article['date_download']=datetime.now()
    article['download_via'] = "Direct2" #change
    article['source_domain'] = source

    
    # insert fixes from custom parser
    article['maintext'] = hvg_story(soup)['maintext']
    article['title'] = hvg_story(soup)['title']
    article['url'] = url
    print('Title is:', article['title'])
    print('Date is:', article['date_publish'])
    print('URL is:', article['url'])



    ## Inserting into the db
    try:
        year = article['date_publish'].year
        month = article['date_publish'].month
        colname = f'articles-{year}-{month}'
        #print(article)
    except:
        colname = 'articles-nodate'

    try:
        # Inserting article into the db:
        db[colname].insert_one(article)
        # count:
        url_count = url_count + 1

        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
    except DuplicateKeyError:
        print("DUPLICATE! Not inserted.")




print("Done inserting ", url_count, "collected urls from ",  source, " into the db.")

##########################################################



baseurl2 = 'https://hvg.hu/itthon/'
links = []
for i in range(1, 150): ## There were 10916 pages when scraped. So the first x - 10916 pages need to be scraped next time.
    linkpageURL = baseurl2 + str(i) + '?ver=1'
    print(linkpageURL)
    reqs = requests.get(linkpageURL, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    for a in soup.find_all('a', href=True):
        if '/gazdasag/' in a['href'] or 'itthon' in a['href'] or '/vilag/' in a['href']:
            if '?ver=1' in a['href']:
                continue

            final_link = 'https://hvg.hu' + a['href']
            links.append(final_link)
       

clean_links2 = list(set(links))




## INSERTING IN THE DB:
url_count = 0
for url in clean_links2:
    if url == "":
        continue
    else:
        if url == None:
            continue
    
    try:
         #response = requests.get(url, headers=headers)
        response = scraper.get(url)
        #article = NewsPlease.from_url(url).__dict__
        article = NewsPlease.from_html(scraper.get(url).text).__dict__
    except:
        time.sleep(0.5)
        try:
            #response = requests.get(url, headers=headers)
            response = scraper.get(url)
            article = NewsPlease.from_html(scraper.get(url).text).__dict__
            #article = NewsPlease.from_url(url).__dict__
        except:
            continue


    soup = BeautifulSoup(response.text, 'html.parser')
       
    # add on some extras
    article['date_download']=datetime.now()
    article['download_via'] = "Direct2" #change
    article['source_domain'] = source

    
    # insert fixes from custom parser
    article['maintext'] = hvg_story(soup)['maintext']
    article['title'] = hvg_story(soup)['title']
    article['url'] = url
    print('Title is:', article['title'])
    print('Date is:', article['date_publish'])
    print('URL is:', article['url'])


    ## Inserting into the db
    try:
        year = article['date_publish'].year
        month = article['date_publish'].month
        colname = f'articles-{year}-{month}'
        #print(article)
    except:
        colname = 'articles-nodate'

    try:
        # Inserting article into the db:
        db[colname].insert_one(article)
        # count:
        url_count = url_count + 1

        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
    except DuplicateKeyError:
        print("DUPLICATE! Not inserted.")




print("Done inserting ", url_count, "collected urls from ",  source, " into the db.")


#########################################################



baseurl3 = 'https://hvg.hu/vilag/'
links = []
for i in range(1, 90): ##There were 6722 pages when scraped. So the first x - 6722 pages need to be scraped next time.
    linkpageURL = baseurl3 + str(i) + '?ver=1'
    print(linkpageURL)
    reqs = requests.get(linkpageURL, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    for a in soup.find_all('a', href=True):
        if '/gazdasag/' in a['href'] or 'itthon' in a['href'] or '/vilag/' in a['href']:
            if '?ver=1' in a['href']:
                continue

            final_link = 'https://hvg.hu' + a['href']
            links.append(final_link)
       

clean_links3 = list(set(links))


  

print('TOTAL LINKS:', len(links))


## INSERTING IN THE DB:
url_count = 0
for url in clean_links3:
    if url == "":
        continue
    else:
        if url == None:
            continue
    
    try:
        #response = requests.get(url, headers=headers)
        response = scraper.get(url)
        #article = NewsPlease.from_url(url).__dict__
        article = NewsPlease.from_html(scraper.get(url).text).__dict__

    except:
        time.sleep(0.5)
        try:
            #response = requests.get(url, headers=headers)
            response = scraper.get(url)
            #article = NewsPlease.from_url(url).__dict__
            article = NewsPlease.from_html(scraper.get(url).text).__dict__

        except:
            continue


    soup = BeautifulSoup(response.text, 'html.parser')
       
    # add on some extras
    article['date_download']=datetime.now()
    article['download_via'] = "Direct2" #change
    article['source_domain'] = source

    
    # insert fixes from custom parser
    article['maintext'] = hvg_story(soup)['maintext']
    article['title'] = hvg_story(soup)['title']
    article['url'] = url
    print('Title is:', article['title'])
    print('Date is:', article['date_publish'])
    print('URL is:', article['url'])


    ## Inserting into the db
    try:
        year = article['date_publish'].year
        month = article['date_publish'].month
        colname = f'articles-{year}-{month}'
        #print(article)
    except:
        colname = 'articles-nodate'

    try:
        # Inserting article into the db:
        db[colname].insert_one(article)
        # count:
        url_count = url_count + 1

        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
    except DuplicateKeyError:
        print("DUPLICATE! Not inserted.")



print("Done inserting ", url_count, "collected urls from ",  source, " into the db.")
