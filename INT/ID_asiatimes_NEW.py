#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to scrape articles from https://asiatimes.com/2024/11/
and insert them into MongoDB, categorizing by November 2024.
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import re

# Database connection
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
source = 'asiatimes.com'

# Set headers for requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
}

# Base URL for December 2024
base_url = "https://asiatimes.com/2024/12/"

# Function to extract article URLs from the main URL
def get_article_urls(main_url):
    print(f"Scraping main URL: {main_url}")
    response = requests.get(main_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    article_links = []

    # Extract links to articles (adjust selector as per the website structure)
    for link in soup.find_all('a', href=True):
        url = link['href']
        # Ensure the URL is part of the target month and matches the correct format
        if re.match(r'https://asiatimes\.com/2024/12/.+', url):
            article_links.append(url)

    return list(set(article_links))  # Deduplicate URLs

# Scrape articles and insert them into the database
def scrape_articles(urls):
    url_count = 0
    for url in urls:
        try:
            print(f"Scraping article: {url}")
            response = requests.get(url, headers=headers)
            article = NewsPlease.from_html(response.text, url=url).__dict__
            article['date_download'] = datetime.now()
            article['download_via'] = "Direct"
            article['source_domain'] = source

            # Determine collection name based on November 2024
            colname = 'articles-2024-12'

            # Insert into MongoDB
            try:
                db[colname].insert_one(article)
                url_count += 1
                print(f"Inserted into '{colname}': {article['title'][:20]} ...")
            except DuplicateKeyError:
                print(f"Duplicate article, not inserted: {url}")
        except Exception as e:
            print(f"Error scraping {url}: {e}")

    print(f"Total articles scraped and inserted: {url_count}")

# Main execution
if __name__ == "__main__":
    # Fetch all article URLs from the main November 2024 page
    article_urls = get_article_urls(base_url)

    # Log the total number of articles found
    print(f"Total unique articles found: {len(article_urls)}")

    # Scrape articles and insert them into the database
    scrape_articles(article_urls)
