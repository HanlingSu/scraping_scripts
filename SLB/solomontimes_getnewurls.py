

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


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'solomontimes.com'
direct_URLs = []
base = 'https://www.solomontimes.com/news/latest/'

for year in range(2025, 2026):
    for month in range(1, 2):
        url = base + str(year) + '/' +str(month)
        print('Scraping from ', url, ' ...')
        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
        req = requests.get(url, headers = hdr)
        soup = BeautifulSoup(req.content)
        item = soup.find_all('section', {'class' : 'article-list-item'})

        for i in item:
            direct_URLs.append(i.find('a')['href'])
    direct_URLs = list(set(direct_URLs))
    print(f'Now scraped {len(direct_URLs)} articles from year {str(year)}.')


blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

direct_URLs = ['https://www.solomontimes.com' + i for i in direct_URLs]

final_result = direct_URLs.copy()
print('Total number of urls found: ', len(final_result))


url_count = 0
processed_url_count = 0
for url in final_result:
    if url:
        # we need to modify the url since there is a typo in scraped urls.
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            response = requests.get(url, headers=header)
            # process
            article = NewsPlease.from_html(response.text, url=url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            

            ## Implementing blacklisting using category info:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            try:
                category = soup.find('div', {'class' : 'tags'}).text.strip()
            except:
                category = "News"

            print(category)

            blacklist = ['Sports']
            if any(substr in category for substr in blacklist):
                article['date_publish'] = None
                article['title'] = "From uninterested category"
                article['maintext'] = None

            print("newsplease date: ", article['date_publish'])
            print("newsplease title: ", article['title'])
            
            if article['maintext']:
                print("newsplease maintext: ", article['maintext'][:50])

                


      
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                
                colname = f'articles-{year}-{month}'
                #print(article)
            except:
                colname = 'articles-nodate'
            #print("Collection: ", colname)
            try:
                #TEMP: deleting the stuff i included with the wrong domain:
                #myquery = { "url": final_url, "source_domain" : 'web.archive.org'}
                #db[colname].delete_one(myquery)
                # Inserting article into the db:
                db[colname].insert_one(article)
                # count:
                if colname != 'articles-nodate':
                    url_count = url_count + 1
                    print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                db['urls'].insert_one({'url': article['url']})
            except DuplicateKeyError:
                pass
                print("DUPLICATE! UPDATED.")
                
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')
 
    else:
        pass

print("Done inserting", url_count, "manually collected urls from",  source, "into the db.")
