
from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from random import randint, randrange
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import json
import time
import re
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

hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

source = 'haqqin.az'
base = 'https://haqqin.az/news/'

direct_URLs = []
url_count = 0
processed_url_count = 0

start = 2000
end =115712
for i in range( start, end):

    
    url = base + str(i)
    print(url)

    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            # process
            article = NewsPlease.from_html(scraper.get(url).text).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            # custom parser
            soup = BeautifulSoup(scraper.get(url).text)
            
            
            
            print("newsplease title: ", article['title'])
            try:
                maintext = ''
                for i in soup.find('div', {'class' : 'article-block'}).find_all('p'):
                    maintext +=i.text
                article['maintext'] = maintext.strip()
            except:
                article['maintext'] = soup.find('div', {'class' : 'article-block'}).text.strip()


            print("newsplease maintext: ", article['maintext'][:50])
        
            print("newsplease date: ",  article['date_publish'])
        
        
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
                db[colname].delete_one( {'url' : url })
                db[colname].insert_one(article)
                pass
                print("DUPLICATE! Updated.")
                
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', end-start, 'articles have been processed ...\n')
    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
