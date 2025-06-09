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
from urllib.parse import urljoin

hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p


source = 'portail.cder.dz'
base = "https://portail.cder.dz"
url_count = 0
processed_url_count = 0
len_final_result = 0

direct_URLs = set()

MAX_PAGES = 10 
for year in range(2019, 2026):
    year_str = str(year)
    for month in range(1, 13):
        month_str = str(month).zfill(2)
    
        date_str = f"{year_str}-{month_str}"
        link = f"{base}/{year_str}/{month_str}/"
        print("Scraping:", link)

        direct_URLs = []

        for p in range(1, MAX_PAGES + 1):
            if p == 1:
                link = f"{base}/{year_str}/{month_str}/"
            else:
                link = f"{base}/{year_str}/{month_str}/page/{p}/"
            print("Scraping:", link)

            try:
                resp = requests.get(link, headers=hdr, verify=False, timeout=10)
                if resp.status_code == 404:
                    print("→ 404, stop paging this month")
                    break
                page_soup = BeautifulSoup(resp.text, 'html.parser')
            except Exception as e:
                print("Request error on page:", link, "-", e)
                break

            # collect URLs on this page
            page_urls = []
            for entry in page_soup.find_all('h2', {'class': 'entry-title'}):
                a_tag = entry.find('a')
                if a_tag and 'href' in a_tag.attrs:
                    page_urls.append(urljoin(base, a_tag['href']))

            if not page_urls:
                print("→ no articles on this page, stop paging this month")
                break

            direct_URLs.extend(page_urls)

        final_result = direct_URLs
        len_final_result += len(final_result)

        for url in final_result:
            if url:
                print(url, "FINE")
                try:
                    # Load article page
                    article_html = requests.get(url, headers=hdr, timeout=10, verify=False).text
                    soup = BeautifulSoup(article_html, 'html.parser')

                    # Use NewsPlease
                    article = NewsPlease.from_html(article_html, url=url).__dict__
                    article['date_download'] = datetime.now()
                    article['download_via'] = "Direct2"
                    article['source_domain'] = source
                    article['url'] = url
                    article['environmental'] = True

                    # Date extraction from known structure
                    try:
                        article['date_publish'] = dateparser.parse(date_str)
                        print("Date parsed from URL:", article['date_publish'])
                    except:
                        article['date_publish'] = None

                    # Extract article main text manually
                    try:
                        maintext = soup.find('div', {'class': 'entry-content clearfix'}).find_all('p')
                        article['maintext'] = "\n".join(m.get_text(strip=True) for m in maintext if m.get_text(strip=True))
                    except:
                        article['maintext'] = article.get('maintext', '')

                    print("newsplease date:", article['date_publish'])
                    print("newsplease title:", article.get('title'))
                    print("newsplease maintext:", article.get('maintext', '')[:50])

                    # Insert to DB
                    try:
                        year = article['date_publish'].year
                        month = article['date_publish'].month
                        colname = f'articles-{year}-{month}'
                    except:
                        colname = 'articles-nodate'

                    try:
                        db[colname].insert_one(article)
                        db['urls'].insert_one({'url': article['url']})
                        url_count += 1
                        print("Inserted in", colname, "- number of URLs so far:", url_count)
                    except DuplicateKeyError:
                        print("DUPLICATE! Not inserted.")
                except Exception as err:
                    print("ERROR scraping article:", err)

                processed_url_count += 1
                print(f"\n{processed_url_count}/{len_final_result} articles processed...\n")

print("Done inserting", url_count, "manually collected URLs from", source, "into the DB.")