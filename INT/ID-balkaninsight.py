import cloudscraper
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []

# Base sitemap URL for post-sitemap97.xml only
base = "https://balkaninsight.com/post-sitemap97.xml"

# Use cloudscraper to bypass Cloudflare
scraper = cloudscraper.create_scraper()
req = scraper.get(base)

# Check the response content to ensure we get the XML instead of an HTML error page
print("Sitemap content (first 1000 characters):")
print(req.text[:1000])  # Print the first 1000 characters of the response for debugging

# Parse the XML content with BeautifulSoup
soup = BeautifulSoup(req.content, 'xml')

# Try to find <loc> tags containing the article URLs
loc_tags = soup.find_all(lambda tag: tag.name.endswith('loc'))

print(f"Found {len(loc_tags)} <loc> tags in the sitemap.")

# Append URLs from <loc> tags (if any)
for i in loc_tags:
    direct_URLs.append(i.text.strip())

# Debugging output to show collected URLs
print("Collected ", len(direct_URLs), " article URLs from the sitemap.")
print("Sample URLs: ", direct_URLs[:5])

# Remove duplicate URLs
direct_URLs = list(set(direct_URLs))

final_result = direct_URLs.copy()
print("Final result: ", len(final_result))
print("Sample URLs: ", final_result[:5])

url_count = 0
processed_url_count = 0
source = 'https://balkaninsight.com'

# Define the date range for September 2024
start_date = datetime(2024, 10, 1)
end_date = datetime(2024, 10, 30, 23, 59, 59)

# Scrape and process each URL
for url in final_result:
    if url:
        print(url, "FINE")
        try:
            # Send request to the article URL
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            response = scraper.get(url, headers=header)

            # Extract article information using NewsPlease
            article = NewsPlease.from_html(response.text, url=url).__dict__
            article['date_download'] = datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source

            # Check if the article's publish date is in September 2024
            if article['date_publish']:
                publish_date = article['date_publish']
                print('Article published on:', publish_date)

                # Filter articles published between September 1, 2024, and September 30, 2024
                if start_date <= publish_date <= end_date:
                    print('Article is from September 2024, processing it.')

                    # Process article (title, main text, etc.)
                    if article['title']:
                        print('Title: ', article['title'])
                    if article['maintext']:
                        print('Maintext preview: ', article['maintext'][:50])

                    # Determine the collection name based on the publish date
                    try:
                        year = publish_date.year
                        month = publish_date.month
                        colname = f'articles-{year}-{month}'
                    except:
                        colname = 'articles-nodate'

                    try:
                        # Insert the article into MongoDB
                        db[colname].insert_one(article)
                        url_count += 1
                        print(f"Inserted in {colname} - number of URLs so far: {url_count}")
                        db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        print("DUPLICATE! Not inserted.")
                else:
                    print('Article not from September 2024, skipping.')
            else:
                print('No publish date found, skipping article.')
                
        except Exception as err:
            print("ERRORRRR......", err)
            pass

        processed_url_count += 1
        print(f'\n{processed_url_count} / {len(final_result)} articles processed ...\n')

print(f"Done inserting {url_count} articles from {source} into the DB.")
