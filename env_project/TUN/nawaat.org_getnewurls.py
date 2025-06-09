# Packages:
from pymongo import MongoClient
import re
import bs4
from bs4 import BeautifulSoup
from newspaper import Article
from dateparser.search import search_dates
import dateparser
import requests
from urllib.parse import quote_plus

import urllib.request
import time
from time import time
import random
from random import randint, randrange
from warnings import warn
import json
from pymongo import MongoClient
from urllib.parse import urlparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from pymongo.errors import CursorNotFound
from newsplease import NewsPlease
from dotenv import load_dotenv
import cloudscraper 

hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'nawaat.org'
direct_URLs = set()


for p in range(1, 20):
    link = 'https://nawaat.org/categories/articles/environment/page/' + str(p)
    # link = 'https://nawaat.org/filter/page/' + str(p) +'/?lang%5B0%5D=ar&lang%5B1%5D=fr&lang%5B2%5D=en&theme%5B0%5D=environment' 
    print("Getting urls from: ", link)

    response = requests.get(link, verify=False)
    response.encoding = 'utf-8'

    soup = BeautifulSoup(response.content)
    for i in soup.find_all('h1', {'class':'entry-title'}):
        direct_URLs.add(i.find('a')['href'])
            
    print('Now scraped ', len(direct_URLs), 'articles from previous months ... ')

print('There are ', len(direct_URLs), 'urls')
final_result = list(direct_URLs).copy()


print('The total count of final result is: ', len(final_result))

arabic_months = {
    'جانفي': 'January',
    'فيفري': 'February',
    'مارس': 'March',
    'أفريل': 'April',
    'ماي': 'May',
    'جوان': 'June',
    'جويلية': 'July',
    'أوت': 'August',
    'سبتمبر': 'September',
    'أكتوبر': 'October',
    'نوفمبر': 'November',
    'ديسمبر': 'December'
}

# Function to translate only the arab dates 

def translate_arabic_month(date_text):
    for ar_month, en_month in arabic_months.items():
        if ar_month in date_text:
            return date_text.replace(ar_month, en_month)
    return date_text

url_count = 0
processed_url_count = 0
for url in final_result:
        if url:
            print(url, "FINE")
            ## SCRAPING USING NEWSPLEASE:
            try:
                # process
                response = requests.get(url, verify=False)
                soup = BeautifulSoup(response.content)
                article = NewsPlease.from_html(response.text, url=url).__dict__

                # add on some extras
                article['date_download']=datetime.now()
                article['download_via'] = "Direct2"
                article['source_domain'] = source
                article['url'] = url
                article['environmental'] = True

                # Get maintext
                try:
                    maintext = ""
                    
                    # Try different div class options in order of priority
                    main_content_div = (
                        soup.find('div', {'class': 'entry-content'}) or 
                        soup.find('div', {'class': 'entry-content text-right rtl'}) or
                        soup.find('div', {'class': 'entry-content-video text-white'}) or 
                        soup.find('div', {'class': 'entry-content-video text-white  text-right rtl '})    
                    )

                    if main_content_div:
                        paragraphs = main_content_div.find_all('p')
                        for p in paragraphs:
                            if p:
                                maintext += p.get_text(strip=True) + "\n"
                        article['maintext'] = maintext.strip()
                    else:
                        article['maintext'] = ""
                        print(f"Warning: Could not find any known main content div for URL: {url}")

                except Exception as e:
                    article['maintext'] = ""
                    print(f"Error extracting main text: {e}")
                
                # Extract date 
                try:
                    date = soup.find('span', {'class': 'posted-on'}).text.strip()
                    date = translate_arabic_month(date)
                    article['date_publish'] = dateparser.parse(date)
                except: 
                    article['date_publish'] = article['date_publish'] 

                print("newsplease date: ", article['date_publish'])
                print("newsplease title: ", article['title'])
                print("newsplease maintext: ", article['maintext'][:50])

                if article['maintext']:
                    try:
                        year = article['date_publish'].year
                        month = article['date_publish'].month
                        colname = f'articles-{year}-{month}'
                        #print(article)
                    except:
                        colname = 'articles-nodate'
                    #print("Collection: ", colname)
                    try:
                        #TEMP: deleting the stuff i included with the wrong domain:
                        # myquery = { "url": final_url, "source_domain" : 'web.archive.org'}
                        # db[colname].delete_one(myquery)
                        # Inserting article into the db:
                        db[colname].insert_one(article)
                        # count:
                        url_count = url_count + 1
                        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        print("DUPLICATE! Not inserted.")
                else:
                    print(f"Skipping article due to empty maintext: {url}")

            except Exception as err:
                print("ERRORRRR......", err)
                pass
            processed_url_count += 1
            print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

        else:
            pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")