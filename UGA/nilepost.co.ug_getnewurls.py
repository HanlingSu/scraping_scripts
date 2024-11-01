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
import json

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

direct_URLs = []
source = 'nilepost.co.ug'
sitemap_base = 'https://nilepost.co.ug/sitemap'

start = 40
end = start +1
for i in range(start, end):
    sitemap = sitemap_base  + '.xml'
    # print(sitemap)
    hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
    soup = BeautifulSoup(scraper.get(sitemap).text)
    item = soup.find_all('loc')

    for i in item:
        direct_URLs.append(i.text)


    print('Now scraped ', len(direct_URLs), ' articles from previous pages.')


# final_result = direct_URLs.copy()[:500][::-1]
# final_result = direct_URLs.copy()[:250]
# final_result = direct_URLs.copy()[250:500]
# final_result = direct_URLs.copy()[500:750]
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
            # process
            soup = BeautifulSoup(scraper.get(url).text)
            article = NewsPlease.from_html(scraper.get(url).text).__dict__
            # add on some extras
            article['url'] = url
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            # title has no problem

            try:
                category = soup.find('span', {"class" :"mb-md-3 cat"}).text.strip()
            except:
                category = "News"
            print(category)


            if category in ["Food Hub", "Love Therapist", "Let's Talk About Sex", "Hatmahz Kitchen", "Tour & Travel", "Entertainment", "Homes", "Lifestyle", "Technology", "Ask the Mechanic"\
                            , "Sports", "Place-It", "StarTimes Uganda Premier League", "World Cup", ]:
                article['date_publish'] = None
                article['title'] = 'From uninterested category'
                article['maintext'] = None
                print( article['title'], category)
            else:
                try:
                    maintext = ''
                    for i in soup.find('div', {'class' : 'content-inner'}).find_all('p'):
                        maintext += i.text
                    article['maintext'] = maintext.strip()
                except:
                    try:
                        maintext = ''
                        for i in soup.find('div', {'class' : 'content-inner'}).find_all('div', {'class' : None}):
                            maintext += i.text
                        article['maintext'] = maintext.strip()
                    except:
                        article['maintext'] =  article['maintext']

                if not article['date_publish']:
                    try:
                        date =  json.loads(soup.find_all('script', {'type' : "application/ld+json"})[1].contents[0], strict=False)['datePublished']
                        article['date_publish'] = dateparser.parse(date)
                    except:
                        article['date_publish'] = article['date_publish']

                print("newsplease date: ", article['date_publish'])
                print("newsplease title: ", article['title'])
                print("newsplease maintext: ", article['maintext'][:50])
                
            
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'articles-{year}-{month}'
                
            except:
                colname = 'articles-nodate'
                
            # Inserting article into the db:
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'articles-{year}-{month}'
                # print(article)
            except:
                colname = 'articles-nodate'
            print("Collection: ", colname)
            
            try:
                db[colname].insert_one(article)
                # count:
                if colname != 'articles-nodate':
                    url_count = url_count + 1
                    print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                db['urls'].insert_one({'url': article['url']})
            except DuplicateKeyError:
                db[colname].delete_one({'url' : url})
                db[colname].insert_one(article)
                print("DUPLICATE! Updated.")


        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n', url_count, 'articles inserted')
        # if processed_url_count % 300 == 0:
        #     time.sleep(500)
  
    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
