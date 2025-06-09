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
import nepali_datetime as ndt

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
from nepali_datetime import date as nepali_date
from datetime import date, datetime, time
scraper = cloudscraper.create_scraper(
    browser ={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    } 
)

hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'gorkhapatraonline.com'
direct_URLs = set()

for p in range(2, 15):
    link = 'https://gorkhapatraonline.com/categories/earthquake?page=' + str(p)
    print("Getting urls from: ", link)

    response = requests.get(link, verify=False)
    soup = BeautifulSoup(response.content)

    for i in soup.find_all('h2', {'class':'item-title mb-2'}):
        direct_URLs.add(i.find('a')['href'])

    print('Now scraped ', len(direct_URLs), 'articles from previous months ... ')


print('There are ', len(direct_URLs), 'urls')
final_result = list(direct_URLs).copy()

print('The total count of final result is: ', len(final_result))



nepali_to_arabic = {
    '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
    '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
}

def convert_to_arabic(nepali_num_str):
    return ''.join(nepali_to_arabic.get(ch, ch) for ch in nepali_num_str)

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

            # Extract text
            try:
                content = soup.find('div', {'class': 'single-blog-content'})
                text_details = content.find_all('div', {'class': 'blog-details'})
                maintext = ""

                for t in text_details:
                    paragraphs = t.find_all('p')
                    for p in paragraphs:
                        maintext += p.get_text(separator=' ', strip=True) + " "
            
                article['maintext'] = maintext.strip()
            except Exception as e:
                article['maintext'] = ""
                print('Error extracting text', e)
  
            # Extract date
            try:
                nepali_date_str = soup.find_all('div', {'class' : 'd-flex align-items-center share-inline-block mb-3'})[1].text.strip().split(',')[0]
                # Split the Nepali date parts
                print(nepali_date_str)

                day_str, month_ne, year_str = nepali_date_str.split()

                # Convert numerals
                day = int(convert_to_arabic(day_str))
                year = int(convert_to_arabic(year_str))
                nepali_months = {
                    'बैशाख': 1, 'वैशाख': 1,
                    'जेठ': 2,
                    'असार': 3, 'आषाढ': 3, 'असार': 3,  # both spellings
                    'साउन': 4, 'श्रावण': 4,
                    'भदौ': 5, 'भाद्र': 5,
                    'आशोज': 6, 'आश्विन': 6,
                    'कात्तिक': 7, 'कार्तिक': 7,
                    'मंसिर': 8, 'मार्ग': 8,
                    'पौष': 9, 'पुस': 9,
                    'माघ': 10,
                    'फागुन': 11, 'फाल्गुण': 11,
                    'चैत': 12, 'चैत्र': 12
                }

                month = nepali_months[month_ne]
                print(month)
                # Create Nepali date object
                nepali_date = ndt.date(year, month, day)

                # Convert to Gregorian
                gregorian_date = nepali_date.to_datetime_date()
                print(gregorian_date)

                article['date_publish'] = datetime.combine(gregorian_date, time())

            except Exception as e:
                print("Date parsing error:", e)
                article['date_publish'] = None

            print("newsplease date: ", article['date_publish'])
            print("newsplease title: ", article['title'])
            print("newsplease maintext: ", article['maintext'][:90])

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
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')
   
    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")

