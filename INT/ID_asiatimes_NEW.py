#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to crawl asiatimes.com and scrape all articles from December 2024.
Inserts into MongoDB collection: articles-2024-12
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
from urllib.parse import urljoin, urlparse
import re

# MongoDB connection
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
source = 'asiatimes.com'
colname = 'articles-2024-12'

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
}

# Match only full article URLs for December 2024
ARTICLE_REGEX = re.compile(r'https://asiatimes\.com/2024/12/[^/]+/?$')

# Crawling logic
def crawl_for_december_articles(start_url, max_depth=2):
    to_visit = [(start_url, 0)]
    visited = set()
    found_articles = set()

    while to_visit:
        url, depth = to_visit.pop(0)
        if url in visited or depth > max_depth:
            continue

        visited.add(url)
        print(f"Crawling: {url} (depth {depth})")

        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            for link in soup.find_all('a', href=True):
                href = urljoin(url, link['href'])
                # Normalize and restrict to asiatimes.com
                if not href.startswith('https://asiatimes.com'):
                    continue
                href = href.split('#')[0]  # Remove fragment identifiers

                # If it's a December 2024 article, store it
                if ARTICLE_REGEX.match(href):
                    found_articles.add(href)
                else:
                    # If it's not an article, crawl it if not visited
                    if href not in visited:
                        to_visit.append((href, depth + 1))

        except Exception as e:
            print(f"Failed to crawl {url}: {e}")

    return list(found_articles)

# Article scraping logic
def scrape_and_insert_articles(article_urls):
    url_count = 0
    for url in article_urls:
        try:
            print(f"Scraping article: {url}")
            response = requests.get(url, headers=headers)
            article = NewsPlease.from_html(response.text, url=url).__dict__

            article['date_download'] = datetime.now()
            article['download_via'] = "Recursive Crawl"
            article['source_domain'] = source


            try:
                db[colname].insert_one(article)
                url_count += 1
                print(f"Inserted: {article.get('title', '')[:50]} ...")
            except DuplicateKeyError:
                print(f"Duplicate article skipped: {url}")

        except Exception as e:
            print(f"Error scraping {url}: {e}")

    print(f"Total articles scraped and inserted: {url_count}")

# Main
if __name__ == "__main__":
    homepage = "https://asiatimes.com/"
    article_urls = crawl_for_december_articles(homepage, max_depth=2)

    print(f"Total unique December 2024 articles found: {len(article_urls)}")
    scrape_and_insert_articles(article_urls)
