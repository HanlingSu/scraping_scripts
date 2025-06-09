#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import sys
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
from datetime import datetime

# Database connection
uri = 'mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true'
db = MongoClient(uri).ml4p

# Headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# Define source
source = 'timesofindia.indiatimes.com'

# Months to scrape (January, February, March 2025)
TARGET_MONTHS = ["-January", "-February", "-March"]
TARGET_YEAR = "2025"

def timesofindia_story(soup):
    """Extracts title, main text, and date from Times of India articles."""
    hold_dict = {}

    # Extract Title
    try:
        article_title = soup.find("title").text
        hold_dict['title'] = article_title
    except:
        hold_dict['title'] = None

    # Extract Main Text
    try:
        maintext_contains = soup.find("meta", {"property":"og:description"})
        hold_dict['maintext'] = maintext_contains['content']
    except:
        hold_dict['maintext'] = None

    # Extract Date
    try:
        date_contains = soup.find("meta", {"itemprop":"datePublished"})
        hold_dict['date_publish'] = datetime.strptime(date_contains['content'], '%Y-%m-%d')
    except:
        hold_dict['date_publish'] = None

    return hold_dict

def get_sitemap_urls():
    """Extracts sitemap URLs for January, February, and March 2025."""
    siteurls = []
    sitemap_url = "https://timesofindia.indiatimes.com/staticsitemap/toi/sitemap-index.xml"
    
    print("Extracting sitemap links from:", sitemap_url)
    reqs = requests.get(sitemap_url, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    for link in soup.findAll('loc'):
        found_url = link.text
        if any(month in found_url for month in TARGET_MONTHS) and TARGET_YEAR in found_url:
            print("Found sitemap:", found_url)
            siteurls.append(found_url)

    print("Total sitemaps found for Jan-Mar 2025:", len(siteurls))
    return siteurls

def extract_article_urls(siteurls):
    """Extracts article URLs from the specified sitemaps."""
    article_urls = []
    
    for sitemap in siteurls:
        print("Extracting articles from:", sitemap)
        reqs = requests.get(sitemap, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        for link in soup.findAll('loc'):
            url = link.text
            if "timesofindia.indiatimes.com" in url:
                article_urls.append(url)

    # Remove duplicate URLs
    return list(set(article_urls))

def scrape_and_store_articles(article_urls):
    """Scrapes articles from URLs and inserts them into MongoDB."""
    url_count = 0
    for url in article_urls:
        try:
            print(f"Scraping: {url}")
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Scrape using NewsPlease & custom parser
            article = NewsPlease.from_html(response.text, url=url).__dict__
            parsed_data = timesofindia_story(soup)

            # Assign scraped data
            article['title'] = parsed_data['title']
            article['maintext'] = parsed_data['maintext']
            article['date_publish'] = parsed_data['date_publish']
            article['date_download'] = datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source

            # Filter only articles from Jan, Feb, or Mar 2025
            if article['date_publish'] and article['date_publish'].year == 2025 and article['date_publish'].month in [1, 2, 3]:
                month = article['date_publish'].month
                colname = f'articles-2025-{month}'

                try:
                    db[colname].insert_one(article)
                    url_count += 1
                    print(f"Inserted in {colname}: {article['title'][:50]}")
                except DuplicateKeyError:
                    print("DUPLICATE! Not inserted.")
            else:
                print(f"Skipping {url} - Not from Jan-Mar 2025.")
        
        except Exception as err:
            print("ERROR:", err)
        
        # Avoid hitting rate limits
        time.sleep(1)

    print(f"Done inserting {url_count} articles from {source} into MongoDB.")

def main():
    """Main function to orchestrate the scraping process."""
    sitemap_urls = get_sitemap_urls()
    article_urls = extract_article_urls(sitemap_urls)
    print(f"Total articles found: {len(article_urls)}")
    scrape_and_store_articles(article_urls)

if __name__ == "__main__":
    main()
