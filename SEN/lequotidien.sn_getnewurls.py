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
import cloudscraper

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)

hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

source = 'lequotidien.sn'
sitemap_base = 'https://lequotidien.sn/post-sitemap'

for i in range(2, 3):
    sitemap = sitemap_base + str(i) +'.xml'
    print(sitemap  )
    #header settings
    soup = BeautifulSoup(scraper.get(sitemap).text)
    item = soup.find_all('loc')
    for i in item:
        url = i.text
        direct_URLs.append(url)

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
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            # process
            article = NewsPlease.from_html(scraper.get(url).text).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            article['url'] = url
            # custom parser
            soup = BeautifulSoup(scraper.get(url).text)
            
            try:
                categories = soup.find('div', {'class' : 'entry-category by-category--color small-mb-2'}).text
            except:
                categories = 'News'

            blacklist = ['Sport', 'Football', 'Culture']

            if not any(c in categories for c in blacklist):
                
                print(categories)
                print("newsplease title: ", article['title'])

                print("newsplease maintext: ", article['maintext'][:50])
                
                print("newsplease date: ",  article['date_publish'])
            
            
                try:
                    year = article['date_publish'].year
                    month = article['date_publish'].month
                    if categories == 'Opinions & débats':
                        colname = f'opinion-articles-{year}-{month}'
                    else:
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
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')
        time.sleep(60)
    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
