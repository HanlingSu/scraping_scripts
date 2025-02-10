from bs4 import BeautifulSoup
import requests
import re
from datetime import timedelta, date, datetime
import pandas as pd
import dateparser
from newsplease import NewsPlease
from dotenv import load_dotenv
# Packages:
import re
import pandas as pd
from pymongo import MongoClient
import dateparser
import requests
from pymongo import MongoClient
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
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



final_result = list(pd.read_csv('Downloads/peace-machine/peacemachine/getnewurls/ZAF/soncoza.csv')['0'])


source = 'son.co.za'
url_count = 0
processed_url_count = 0
for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            # process
            article = NewsPlease.from_html(scraper.get(url).text).__dict__

            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            article['url'] = url
            article['language'] = 'af'
            print("newsplease title: ", article['title'])


            ## Fixing Date:
            soup = BeautifulSoup(scraper.get(url).text)
            # Get Date
            try:
                date = soup.find('meta', {'name' : 'publisheddate'})['content']
                article['date_publish'] = dateparser.parse(date).replace(tzinfo=None)      
            except:
                try:
                    date = soup.find('meta', property = 'article:published_time')['content']
                    article['date_publish'] = dateparser.parse(date).replace(tzinfo=None)
                except:
                    article['date_publish'] = None
            print("newsplease date: ", article['date_publish'])
                    
            if not article['maintext']:
                try:
                    maintext = ''
                    for i in soup.find('div', {'class' : 'content'}).find_all('p'):
                        maintext += i.text
                    article['maintext'] = maintext.strip()
                except:
                    maintext = ''
                    for i in soup.find('div' , {'class' : 'article__body NewsArticle'}).find_all('p'):
                        maintext += i.text
                    article['maintext'] = maintext.strip()

            if article['maintext']:
                print('newsplease maintext: ', article['maintext'][:50])
                
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'articles-{year}-{month}'
                #print(article)
            except:
                colname = 'articles-nodate'
            #print("Collection: ", colname)
            try:
                
                # Inserting article into the db:
                db[colname].insert_one(article)
                # count:
                url_count = url_count + 1
                print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                db['urls'].insert_one({'url': article['url']})
            except DuplicateKeyError:
                print("DUPLICATE! Not inserted.")
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
