
# Packages:
from typing import final
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import dateparser
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import re
import time
import cloudscraper
# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
direct_URLs = []
source = 'island.lk'

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)


sitemap_base = 'https://island.lk/wp-sitemap-posts-post-'
for p in range(27, 29):
    sitemap = sitemap_base + str(p) +'.xml'
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = requests.get(sitemap, headers = hdr)
    soup = BeautifulSoup(req.content)
    items = soup.find_all('loc')
    for i in items:
        direct_URLs.append(i.text)
    print(len(direct_URLs))


final_result = direct_URLs.copy()
print(len(final_result))

url_count = 0
processed_url_count = 0
for url in final_result[::-1]:
    if url:
        print(url, "FINE")
        # time.sleep(5)
        ## SCRAPING USING NEWSPLEASE:
        try:
            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            # process
            article = NewsPlease.from_html(scraper.get(url).text).__dict__

            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            print("newsplease date: ", article['date_publish'])
            print("newsplease title: ", article['title'])
            print("newsplease maintext: ", article['maintext'][:50])
 
          
            soup = BeautifulSoup(scraper.get(url).text)
            try:
                category = soup.find('span', {'class' : 'mvp-post-cat left'}).text
            except:
                category = 'News'
            print(category)

            if category in ['Fashion', 'Opinion', 'Editorial', 'Sports', 'Life style', 'advertisements', 'Business']:
                article['title'] = 'From Uninterested Category'
                print(article['title'], category)
                article['date_publish'] = None
                article['maintext'] = None

            # fix maintext
            try:
                soup.find('div', {'id' : 'mvp-content-main'})
                maintext = ''
                for i in soup.find('div', {'id' : 'mvp-content-main'}).find_all('p'):
                    if i.text[:2].lower() == 'by':
                        continue
                    else: 
                        maintext += i.text
            
                article['maintext'] = maintext.strip()              
            except:
                maintext = None
                article['maintext']  = None

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
                if colname !=  'articles-nodate':
                    db[colname].insert_one(article)
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