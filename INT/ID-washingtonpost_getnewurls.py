from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import requests
from pymongo import MongoClient
from datetime import datetime
from newsplease import NewsPlease
from pymongo.errors import DuplicateKeyError

# Set up headless browser options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize the WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Target sitemap URL
sitemap_url = 'https://www.washingtonpost.com/sitemap/2024/09.xml'

# Fetch the sitemap using Selenium
print(f"Processing sitemap: {sitemap_url}")
driver.get(sitemap_url)

# Parse the sitemap XML content
soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()

# Extract URLs from the sitemap
urls = [link.text for link in soup.findAll('loc')]
print(f"Found {len(urls)} article URLs.")

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# Filter and process URLs
list_urls = list(set(urls))
print(f"Total number of USABLE URLs found for August 2024: {len(list_urls)}")

url_count = 0
for url in list_urls:
    if url:
        print(f"Processing URL: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            article = NewsPlease.from_html(response.text, url=url).__dict__
            article['date_download'] = datetime.now()
            article['download_via'] = "Direct2"

            # Check if the article date is in August 2024
            try:
                if article['date_publish'].year == 2024 and article['date_publish'].month == 8:
                    year = article['date_publish'].year
                    month = article['date_publish'].month
                    colname = f'articles-{year}-{month}'
                else:
                    continue  # Skip articles not from August 2024
            except:
                colname = 'articles-nodate'
            
            # Inserting into the db
            try:
                db[colname].insert_one(article)
                url_count += 1
                print(f"Inserted! in {colname} - number of URLs so far: {url_count}")
                db['urls'].insert_one({'url': article['url']})
            except DuplicateKeyError:
                print("DUPLICATE! Not inserted.")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
        except Exception as err: 
            print(f"ERRORRRR...... {err}")
        finally:
            time.sleep(1)

print(f"Done inserting {url_count} URLs from August 2024 into the db.")
