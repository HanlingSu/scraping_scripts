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
import json
# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []
source = 'cartamz.com'
base = 'https://cartamz.com/index.php/'
category = ['crime', 'politica', 'economia-e-negocios', 'sociedade', 'cartaz']
page_start = [0,0,0,0,0]
page_end = [1, 280, 128, 190, 54]

for c, ps, pe in zip(category, page_start, page_end):
    for p in range(ps+1, pe+1, 6):
        url = base + c + '?start=' + str(p)
        print(url)
        hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'} #header settings
        req = requests.get(url, headers = hdr)
        soup = BeautifulSoup(req.content)
        item = soup.find_all('h3', {'class':"catItemTitle"})
        for i in item:
            direct_URLs.append(i.find('a')['href'])

        print('Now scraped ', len(direct_URLs), ' articles from previous pages.')

final_result = ['https://cartamz.com' + i for i in direct_URLs]
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
            response = requests.get(url, headers=header)
            # process
            article = NewsPlease.from_html(response.text, url=url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            # title, date, and main text has no problem
           
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