import requests
import bs4
from bs4 import BeautifulSoup

def count_articles(base_url, pages):
    total_articles = 0

    for page in range(1, pages + 1):
        url = f"{base_url}/{page}/"
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            
            articles = soup.find_all('article') 
            total_articles += len(articles)
            
            print(f"Page {page}: {len(articles)} articles found")
        else:
            print(f"Failed to access Page {page}, Status Code: {response.status_code}")
    
    print(f"Total Articles: {total_articles}")
    return total_articles


base_url = "https://tribuneonlineng.com/category/ecoscope/page"

# Number of pages to scrape
pages = 17

# Get total article count
count_articles(base_url, pages)

