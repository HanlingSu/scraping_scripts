import requests
from datetime import timedelta, date, datetime
import newspaper
import pandas as pd
import dateparser
from pandas.core.common import flatten
from newsplease import NewsPlease
from dotenv import load_dotenv
# Packages:
import pandas as pd

from pymongo import MongoClient
from bs4 import BeautifulSoup
from dateparser.search import search_dates
import dateparser
import requests
from urllib.parse import quote_plus

from random import randint, randrange
from warnings import warn
from pymongo import MongoClient
from urllib.parse import urlparse
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
from dotenv import load_dotenv
import cloudscraper
import re

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)
source = 'iol.co.za'

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

final_result = list(pd.read_csv('Downloads/peace-machine/peacemachine/getnewurls/ZAF/iolcoza.csv')['0'])


blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
final_result = [word for word in final_result if not blacklist.search(word)]


url_count = 0
processed_url_count = 0
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)


for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            response = requests.get(url, headers=header)
            # process
            article = NewsPlease.from_html(scraper.get(url).text).__dict__

            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            article['url'] = url

            ## Fixing Date:
            soup = BeautifulSoup(scraper.get(url).text, 'html.parser')
            
            try:
                article['title'] = soup.find('meta', {'property' : 'og:title'})['content'] 
            except:
                try:
                    article['title'] = soup.title.text
                except:
                    article['title'] = None
            print("newsplease title: ", article['title'])
        
            try:
                date = soup.find('meta', {'itemprop' : 'datePublished'})['content']
                article['date_publish'] = dateparser.parse(date).replace(tzinfo = None)
            except:
                try:
                    date = soup.find('p', {'color':"meta", 'class':"sc-cIShpX eUsufX"}).text
                    date = date.replace('Published', '')
                    article['date_publish'] = dateparser.parse(date).replace(tzinfo = None)
                except:
                    article['date_publish'] = None
            print('newsplease date:', article['date_publish'])
            
            try:
                maintext = soup.find('div', {'class' : 'Article__StyledArticleContent-sc-uw4nkg-0 boyytX article-content'}).text

                article['maintext'] = maintext.strip()
            except:
                article['maintext'] = article['maintext']
            print("newsplease maintext: ", article['maintext'][:50])

            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'articles-{year}-{month}'
                #print(article)
            except:
                colname = 'articles-nodate'

            try:
                db[colname].insert_one(article)
                # count:
                url_count = url_count + 1
                print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                # db['urls'].insert_one({'url': article['url']})
            except DuplicateKeyError:
                # db['urls'].delete_one({'url': article['url']})

                # db[colname].delete_one( { "url": url, "source_domain" : source})
                # db[colname].insert_one(article)


                print("DUPLICATE! Pass.")
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
