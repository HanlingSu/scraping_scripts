# created by Hanling, Sep 2024

# Packages:
from typing import final
from unicodedata import category
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import dateparser
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import re
import json

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
direct_URLs = []
source = 'asia.nikkei.com'

direct_URLs = []

categories= ['Location/East-Asia/China', 'Location/East-Asia/Hong-Kong', 'Location/East-Asia/Taiwan', 'Location/East-Asia/Mongolia',\
 'Location/East-Asia/Japan', 'Location/East-Asia/South-Korea', 'Location/East-Asia/Macao', 'Location/Southeast-Asia', 'Location/South-Asia',\
 'Location/Oceania', 'Location/Central-Asia', 'Location/Rest-of-the-World']
                #main       immediate news  local news          
page_start = [1, 1, 1, 1, 1, 1, 1,1 ,1 ,1, 1, 1, 1, 1  ]
page_end = [40, 10, 10, 1, 40, 20, 3, 4, 40, 20, 20, 1, 40 ]
# only change before each update

for c, ps, pe in zip(categories, page_start, page_end):
    for i in range(ps, pe+1):
        link = 'https://asia.nikkei.com/' + c + '?page=' + str(i)
        print(link)
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = requests.get(link, headers = hdr)
        soup = BeautifulSoup(req.content)
        items = soup.find_all('h4'  )
        for item in items:
            try:
                direct_URLs.append(item.find('a')['href'])
            except:
                pass
        direct_URLs = list(set(direct_URLs))
   
        print('Now collected ', len(direct_URLs), 'articles from previous pages...')
    
direct_URLs = ['https://asia.nikkei.com' + i for i in direct_URLs]
final_result = direct_URLs.copy()
print(len(final_result))

url_count = 0
processed_url_count = 0
for url in final_result[::-1]:
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
            print("newsplease date: ", article['date_publish'])
            print("newsplease title: ", article['title'])
            # print("newsplease maintext: ", article['maintext'][:50])
 
            ## Fixing Date:
            soup = BeautifulSoup(response.content, 'html.parser')


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
                if colname != "articles-nodate"
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