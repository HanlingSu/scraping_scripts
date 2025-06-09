#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to scrape SCMP articles (Jan, Feb, Mar 2025) 
and insert them into MongoDB.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import dateparser

# Database connection
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
source = "scmp.com"

# Headers for scraping
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
}

# Define months for January, February, March 2025
TARGET_YEAR = 2025
TARGET_MONTHS = [1, 2, 3]  # January, February, March

# Blacklisted URL patterns (skip these categories)
BLACKLIST_PATTERNS = ["/sport/", "/culture/", "/lifestyle/", "/magazines/", "/comment/"]

# Step 1: Get URLs from sitemaps
SITEMAP_URLS = ["https://www.scmp.com/sitemap/articles.xml"]
article_urls = []

def get_article_urls():
    """Extract article URLs from SCMP sitemap."""
    for sitemap_url in SITEMAP_URLS:
        print(f"Extracting from: {sitemap_url}")
        response = requests.get(sitemap_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        for link in soup.find_all('loc'):
            url = link.text
            if "scmp.com" in url and not any(pattern in url for pattern in BLACKLIST_PATTERNS):
                article_urls.append(url)

    print(f"Total unique articles extracted: {len(article_urls)}")

def scrape_articles():
    """Scrape articles and insert them into MongoDB."""
    url_count = {1: 0, 2: 0, 3: 0}  # Track inserted articles per month

    for url in article_urls:
        try:
            print(f"Scraping: {url}")
            response = requests.get(url, headers=headers)
            article = NewsPlease.from_html(response.text, url=url).__dict__

            # Add metadata
            article['date_download'] = datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source

            # Fixing Date
            try:
                contains_date = response.headers.get("Last-Modified")
                article['date_publish'] = dateparser.parse(contains_date) if contains_date else article.get('date_publish', None)
            except:
                pass

            # Ensure the article belongs to Jan, Feb, or Mar 2025
            if article['date_publish'] and article['date_publish'].year == TARGET_YEAR:
                month = article['date_publish'].month
                if month in TARGET_MONTHS:
                    colname = f'articles-{TARGET_YEAR}-{month}'
                    try:
                        db[colname].insert_one(article)
                        url_count[month] += 1
                        print(f"Inserted into '{colname}': {article['title'][:50]} ...")
                    except DuplicateKeyError:
                        print(f"Duplicate article, not inserted: {url}")
                else:
                    print(f"Skipping article {url} - Not from Jan/Feb/Mar 2025.")
            else:
                print(f"Skipping article {url} - No valid date.")

        except Exception as e:
            print(f"Error scraping {url}: {e}")

    print(f"Total articles inserted: January({url_count[1]}), February({url_count[2]}), March({url_count[3]})")

# Main execution
if __name__ == "__main__":
    get_article_urls()
    scrape_articles()
