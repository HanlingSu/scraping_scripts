
###### Packages:
from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from pymongo import MongoClient
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import cloudscraper

import sys
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import dateparser
from pymongo.errors import DuplicateKeyError
from tqdm import tqdm
import re
import sys
import json
import time
    
import json
import pymongo
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

len_final_result = 0
processed_url_count = 0
url_count = 0

source = 'kazpravda.kz'

for i in range(1, 36):
    direct_URLs = []
    sitemap = 'https://kazpravda.kz/sitemap-' + str(i) + '.xml'
    print(sitemap)
    hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    req = requests.get(sitemap, headers = hdr)
    soup = BeautifulSoup(req.content)
    for i in soup.find_all('loc'):
        direct_URLs.append(i.text)
    
    print(len(direct_URLs))
    final_result = direct_URLs.copy()
    len_final_result += len(final_result)

    for url in final_result:
        if url:
            print(url, "FINE")
            ## SCRAPING USING NEWSPLEASE:
            try:
                hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

                req = requests.get(url, headers = hdr)
                soup = BeautifulSoup(req.content)

                article = NewsPlease.from_html(req.text, url=url).__dict__
                # add on some extras
                article['date_download']=datetime.now()
                article['download_via'] = "Direct2"
                article['source_domain'] = source

                    
                try:
                    date = soup.find('meta', property = 'aiturec:datetime')['content']
                    article['date_publish'] = dateparser.parse(date)
                except:
                    date = soup.find('time', {"class" : 'article__date'}).text
                    article['date_publish'] = dateparser.parse(date)

                print("newsplease date: ", article['date_publish'])
                print("newsplease title: ", article['title'])
                print("newsplease maintext: ", article['maintext'][:50])

                try:
                    year = article['date_publish'].year
                    month = article['date_publish'].month
                    colname = f'articles-{year}-{month}'
                    #print(article)
                except:
                    colname = 'articles-nodate'
                #print("Collection: ", colname)
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
                print("ERRORRRR......", err, 'Inserted to error urls ....')
                
                pass
            processed_url_count += 1
            print('\n',processed_url_count, '/', len_final_result, 'articles have been processed ...\n')
    
        else:
            pass


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")



