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
import re
import cloudscraper


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# define scraper
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)

hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


direct_URLs = []
base = 'http://zambianewsnetwork.com/post-sitemap'
source = 'zambianewsnetwork.com'

for i in range(23, 23+1):
    url = base + str(i) + '.xml'
    soup = BeautifulSoup(scraper.get(url).text)
    item = soup.find_all('loc')
    for i in item:
        direct_URLs.append(i.text)

    print(len(direct_URLs))


final_result = direct_URLs.copy()
print(len(final_result))

url_count = 0
processed_url_count = 0
for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            soup = BeautifulSoup(scraper.get(url).text)

            # process
            article = NewsPlease.from_html(scraper.get(url).text).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            article['url'] = url
            # custom parser

            category = set([])
            try:
                for c in soup.find('div', {'class' : 'mg-blog-category'}).text.split('\r\n'):
                    print(c.strip())
                    category.add(c.strip())
            except:
                pass
            print(category)
            
            blacklist = set(['Science', 'Arts Culture', 'Travel'])
            if category.intersection(blacklist):
                print(category.intersection(blacklist))
                article['date_publish'] = None
                article['title'] = 'From uninterested section!'
                article['maintext'] = None
                print(article['title'], category)
            else:
                print("newsplease title: ", article['title'])
                print("newsplease date: ",  article['date_publish'])
                print('newsplease maintext', article['maintext'][:50])
                    
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
                    pass
                    print("DUPLICATE! Not inserted.")
                    
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
