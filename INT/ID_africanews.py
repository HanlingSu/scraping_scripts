import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
from datetime import datetime, timedelta
import time

# Database connection
MONGO_URI = "mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true"
db = MongoClient(MONGO_URI).ml4p

# Source info
SOURCE = "africanews.com"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# Define target months and year
TARGET_YEAR = 2024
TARGET_MONTHS = [12]  # January, February, March

def generate_dates(year, months):
    """Generate all dates for the given year and list of months."""
    all_dates = []
    for month in months:
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        delta = timedelta(days=1)
        all_dates.extend([(start_date + delta * i).strftime("%Y/%m/%d") for i in range((end_date - start_date).days + 1)])

    return all_dates

def extract_article_links(day_url):
    """Extract article URLs from a given day's page."""
    try:
        response = requests.get(day_url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")
        article_links = []

        # Extract all <a> tags with href
        for link in soup.find_all("a", href=True):
            url = link["href"]
            if url.startswith(f"/{TARGET_YEAR}/") and len(url.split("/")) > 4:
                full_url = "https://www.africanews.com" + url
                article_links.append(full_url)

        return list(set(article_links))  # Remove duplicates
    except Exception as e:
        print(f"Error extracting links from {day_url}: {e}")
        return []

def scrape_and_store(url):
    """Scrape article content and insert it into MongoDB."""
    try:
        print(f"Scraping: {url}")
        response = requests.get(url, headers=HEADERS)
        article = NewsPlease.from_html(response.text, url=url).__dict__

        # Add metadata
        article["date_download"] = datetime.now()
        article["download_via"] = "Africanews Scraper"
        article["source_domain"] = SOURCE

        # Extract date from URL
        try:
            parts = url.split("/")
            year, month, day = int(parts[3]), int(parts[4]), int(parts[5])
            article["date_publish"] = datetime(year, month, day)
        except:
            article["date_publish"] = None

        # Determine MongoDB collection
        try:
            if article["date_publish"]:
                colname = f"articles-{article['date_publish'].year}-{article['date_publish'].month}"
            else:
                colname = "articles-nodate"
        except:
            colname = "articles-nodate"

        # Insert article into MongoDB
        try:
            db[colname].insert_one(article)
            print(f"Inserted in {colname}: {article['title'][:50]}...")
        except DuplicateKeyError:
            print("DUPLICATE! Not inserted.")

        # Store URL in 'urls' collection
        db["urls"].insert_one({"url": url})

    except Exception as err:
        print(f"Error scraping {url}: {err}")

def main():
    """Main function to scrape Africanews for January, February, and March 2025."""
    dates = generate_dates(TARGET_YEAR, TARGET_MONTHS)

    all_article_links = []
    for date in dates:
        day_url = f"https://www.africanews.com/{date}/"
        print(f"Checking: {day_url}")

        article_links = extract_article_links(day_url)
        all_article_links.extend(article_links)
        time.sleep(1)  # Avoid rate limiting

    print(f"Total articles found: {len(all_article_links)}")

    for url in all_article_links:
        scrape_and_store(url)
        time.sleep(1)  # Avoid rate limiting

    print(f"Done scraping and inserting articles for {TARGET_YEAR} (Jan-Mar).")

if __name__ == "__main__":
    main()
