# Packages:
from pymongo import MongoClient
from bs4 import BeautifulSoup
from dateparser.search import search_dates
import dateparser
import requests
from urllib.parse import quote_plus
import time
from datetime import datetime
from pymongo.errors import DuplicateKeyError
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from dotenv import load_dotenv
import cloudscraper


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p


scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)

# collect direct URLs from the latest pages on the sitemap (https://balkaninsight.com/sitemap_index.xml)
direct_URLs = []
sitemap_base = 'https://balkaninsight.com/post-sitemap'



for i in range(96, 97):
    sitemap = sitemap_base + str(i) + '.xml'
    print(sitemap)
    hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
    # req = requests.get(sitemap, headers = hdr)
    soup = BeautifulSoup(scraper.get(sitemap).text)
    item = soup.find_all('loc')

    for i in item:
        direct_URLs.append(i.text)


    print('Now scraped ', len(direct_URLs), ' articles from previous sitemaps.')

final_result = list(set(direct_URLs))
print('Total number of urls found: ', len(final_result))


# custom parser and insert into DB
url_count = 0
source = 'balkaninsight.com'
for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            # process
            
            soup = BeautifulSoup(scraper.get(url).text)
            article = NewsPlease.from_html(scraper.get(url).text, url=url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            # title, date and maintext have no problem
            print("newsplease date: ", article['date_publish'])
            print("newsplease title: ", article['title'])
            print("newsplease maintext: ", article['maintext'][:50])
            
            
            # no need for custom parser

            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'articles-{year}-{month}'
                
            except:
                colname = 'articles-nodate'
            
            # Inserting article into the db:
            try:
                db[colname].insert_one(article)
                # count:
                if colname != 'articles-nodate':
                    url_count = url_count + 1
                    print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                db['urls'].insert_one({'url': article['url']})
            except DuplicateKeyError:
                # myquery = { "url": url}
                # db[colname].delete_one(myquery)
                # db[colname].insert_one(article)
                pass
                # print('DUPLICATE! UPDATED!')
                print("DUPLICATE! Not inserted.")
                
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
