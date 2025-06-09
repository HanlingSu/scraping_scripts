# Packages:
import pymongo 
from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import cloudscraper
import pandas as pd
from tqdm import tqdm
import re
import sys
import json
import time
    

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

source = 'thenationonlineng.net'

processed_url_count = 0
url_count = 0
len_final_result = 0

base = 'https://www.theeastafrican.co.ke/service/search/tea/1446352?query=the&channelId=1289144&docType=CMArticle&sortByDate=true&pageNum='

for p in range(1, 100):
    direct_URLs = []

    url = base + str(p)
    hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    req = requests.get(url, headers = hdr)
    soup = BeautifulSoup(req.content)

    for i in soup.find_all('li', {'class' : 'search-result'}):
        direct_URLs.append(i.find('a')['href'])
        final_result = ['https://www.theeastafrican.co.ke' + i for i in direct_URLs]
        print(final_result)
        len_final_result += len(final_result)

        for url in final_result:
            if url:
                print(url, "FINE")
                ## SCRAPING USING NEWSPLEASE:
                try:
                    #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
                    response = requests.get(url, headers=hdr)
                    article = NewsPlease.from_html(response.text, url=url).__dict__

                    # add on some extras
                    article['date_download']=datetime.now()
                    article['download_via'] = "Direct2"
                    article['source_domain'] = source
 
                    soup = BeautifulSoup(response.content, 'html.parser')



                    # fix date
                    try:
                        date = soup.find('meta', property = 'article:published_time')['content']
                        article['date_publish'] = dateparser.parse(date).replace(tzinfo = None)

                    except:
                        try:
                            date = soup.find('time' , {'class' : 'post-published updated'})['datetime']
                            article['date_publish'] = dateparser.parse(date).replace(tzinfo = None)
                        except:
                            article['date_publish'] =article['date_publish'] 
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
                print('\n',processed_url_count, '/', len_final_result, 'articles have been processed ...\n')
        
            else:
                pass

        print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
        direct_URLs = []