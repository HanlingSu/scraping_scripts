import random
import sys
sys.path.append('../')
import os
import re
from p_tqdm import p_umap
from tqdm import tqdm
from pymongo import MongoClient
import random
from urllib.parse import urlparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from pymongo.errors import CursorNotFound
import requests
from newsplease import NewsPlease
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import dateparser
import pandas as pd

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

## COLLECTING URLS
urls = []

## NEED TO DEFINE SOURCE!
source = 'iwpr.net'

## Define YEAR and MONTH to update:
year_up = 2024
month_up = 8

## STEP 0: URLS FROM SECTIONS:
keywords = ['africa','asia','europe-eurasia','latin-america-caribbean','middle-east-north-africa']
endnumber = ['5','5','5','5','5']

for word in keywords:
    indexword = keywords.index(word)
    endnumberx = endnumber[indexword]

    for i in range(1, int(endnumberx)+1):
        if i == 1:
            url = 'https://iwpr.net/global-voices/' + word
        else:
            url = 'https://iwpr.net/global-voices/' + word + '?region=All&page=' + str(i) 
        
        print(url)

        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        for link in soup.find_all('a'):
            urls.append(link.get('href')) 

## STEP 1: URLS FROM TOPICS

## TOPICS 
keywords = ['elections','war-crimes','conflict-resolution','human-rights','accountability','political-reform','health','international-justice','women','womens-rights','rule-law','civil-society','social-justice','regime','journalism','conflict','detentions','education','media','media-development','diplomacy','protests','refugees','coronavirus','economy']
endnumber = ['3','3','3','3','3','3','3','3','3','3','3','3','3','3','3','3','3','3','3','3','3','3','3','3','3']

for word in keywords:
    indexword = keywords.index(word)
    endnumberx = endnumber[indexword]

    for i in range(0, int(endnumberx)):
        if i == 0:
            url = 'https://iwpr.net/global-voices/topics/' + word
        else:
            url = 'https://iwpr.net/global-voices/topics/' + word + '?page=' + str(i) 
        
        print(url)

        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        for link in soup.find_all('a'):
            urls.append(link.get('href')) 

## STEP 2: URLS FROM COUNTRY SECTIONS (FOR COUNTRIES WITH THEIR OWN SECTION)
countrynames = ['ukraine','belarus','caucasus/armenia','caucasus/azerbaijan','caucasus/georgia','caucasus/karabakh','balkans/bosnia-and-herzegovina','moldova']
endnumber = ['2','3','3','3','3','3','3','3']

for country in countrynames:
    indexword = countrynames.index(country)
    endnumberx = endnumber[indexword]

    for i in range(0, int(endnumberx)):
        if i == 0:
            url = 'https://iwpr.net/global-voices/europe-eurasia/' + country
        else:
            url = 'https://iwpr.net/global-voices/europe-eurasia/' + country + '?page=' + str(i) 
        
        print(url)

        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        for link in soup.find_all('a'):
            urls.append(link.get('href')) 

## STEP 3: URLS FOR COUNTRIES WITHOUT THEIR OWN SECTION: SERBIA AND KOSOVO
countrynames = ['Serbia','Kosovo']
endnumber = ['3','3']

for country in countrynames:
    indexword = countrynames.index(country)
    endnumberx = endnumber[indexword]

    for i in range(0, int(endnumberx)):
        if i == 0:
            url = 'https://iwpr.net/search?keys=' + country + '&sort_bef_combine=created_DESC&locations=All&topics=All&year=&author=&type=All&format=All'
        else:
            url = 'https://iwpr.net/search?keys=' + country +  '&sort_bef_combine=created_DESC&locations=All&topics=All&year=&author=&type=All&format=All&sort_by=created&sort_order=DESC&page=' + str(i) 
        
        print(url)

        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        for link in soup.find_all('a'):
            urls.append(link.get('href')) 

## Preparing URLs for scraping:

# List of unique urls:
unique_urls = list(set(urls))

list_urls = []
for url in unique_urls:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if "https://iwpr.net/" in url:
                newurlx = url
            else:
                newurlx = "https://iwpr.net" + url
            #Appending url: 
            list_urls.append(newurlx) 
print("Total number of USABLE urls found: ", len(list_urls))

## Scraping Articles and Processing them:
url_count = 0
for url in list_urls:
    if url == "":  # Skip if the URL is empty
        pass
    else:
        if url == None:  # Skip if the URL is None
            pass
        else:
            if "iwpr.net" in url:
                print(url, "FINE")
                ## SCRAPING USING NEWSPLEASE:
                try:
                    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                    response = requests.get(url, headers=header)
                    
                    if response.status_code == 200:
                        # Extract article content using NewsPlease
                        article = NewsPlease.from_html(response.text, url=url).__dict__
                        
                        # Check if 'date_publish' is extracted and what type it is
                        if 'date_publish' in article:
                            print(f"Extracted date_publish: {article['date_publish']} for URL: {url}")
                            if isinstance(article['date_publish'], datetime):
                                print(f"date_publish is a valid datetime object: {article['date_publish']}")
                            else:
                                print(f"Warning: date_publish is not a datetime object, it's {type(article['date_publish'])}. Raw value: {article['date_publish']}")
                        else:
                            print(f"No date_publish found for URL: {url}")
                        
                        # Continue with your date check and database insertion
                        year = article.get('date_publish', None)
                        if year:
                            year = article['date_publish'].year
                            month = article['date_publish'].month
                            if year == 2024 and month == 8:
                                colname = f'articles-{year}-{month}'
                                try:
                                    # Inserting article into the db:
                                    db[colname].insert_one(article)
                                    # count:
                                    url_count += 1
                                    print(f"+TITLE: {article.get('title', 'No title')[0:20]} +MAIN TEXT: {article.get('maintext', 'No text')[0:25]}")
                                    print(f"Date extracted: {article['date_publish']} + Inserted! in {colname} - number of urls so far: {url_count}")
                                    db['urls'].insert_one({'url': article['url']})
                                except DuplicateKeyError:
                                    print("DUPLICATE! Not inserted.")
                            else:
                                print(f"Article skipped. Not from August 2024: {article['date_publish']}")
                        else:
                            print("No date_publish field. Article skipped.")
                    else:
                        print(f"Failed to retrieve URL: {url}. Status code: {response.status_code}")
                except Exception as e:
                    print(f"An error occurred while processing the article: {e}")
            else:
                pass

print("Done processing. Total articles from August 2024 found and inserted: ", url_count)
