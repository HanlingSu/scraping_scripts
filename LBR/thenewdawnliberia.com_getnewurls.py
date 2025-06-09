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

source = 'thenewdawnliberia.com'

# base = 'https://thenewdawnliberia.com/post-sitemap'
# for p in range(34, 35+1):
#     url = base+str(p) +'.xml'
#     req = requests.get(url, headers = headers)
#     soup = BeautifulSoup(req.content)

#     for i in soup.find_all('loc'):
#         direct_URLs.append(i.text)
#     print(len(direct_URLs))

# direct_URLs = pd.read_csv('Downloads/peace-machine/peacemachine/getnewurls/LBR/thenewdawnliberia.csv')['url'][::-1]

category = ['liberia-news', 'features', 'editorial']
page_start = [78, 18, 2]
page_end = [85, 22, 4]
for c, ps, pe in zip(category, page_start, page_end):
    for p in range(ps, pe+2):
        direct_URLs = set()
        time.sleep(10)
        url = 'https://thenewdawnliberia.com/category/' + c + '/page/' +str(p)
        print(url)
        req = requests.get(url, headers = headers)
        soup = BeautifulSoup(req.content)
        for i in soup.find_all('h2', {'class' : 'post-title'}):
            direct_URLs.add(i.find('a')['href'])
        print(len(direct_URLs))

        direct_URLs = ['https://thenewdawnliberia.com' + i for i in direct_URLs]
        final_result = direct_URLs
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

                    soup = BeautifulSoup(response.content, 'html.parser')
                    # category:
                    
                    try:
                        category = soup.find('nav', {'id' : 'breadcrumb'}).text.split('/')[1].strip()
                    except:
                        category = 'News'
                    
                    if category == 'Features':
                        category = soup.find('nav', {'id' : 'breadcrumb'}).text.split('/')[2].strip()
                    print(category)

                    if category in [ 'Sports',  'ORIGINAL LETTER TO GOD',  'Special Feature']:
                        article['maintext'] = None
                        article['date_publish'] = None
                        article['title'] = 'From uninterested category!'
                        print(article['title'], category)
                    else:
                        
                        print("newsplease title: ", article['title'])          
                        print("newsplease maintext: ", article['maintext'][:50])

                        try:
                            date = soup.find('meta', {'property' : 'article:published_time'})['content']
                            article['date_publish'] = dateparser.parse(date)
                        except:
                            date = soup.find('span', {'class' : 'date meta-item tie-icon'}).text
                            article['date_publish'] = dateparser.parse(date)
                        print("newsplease date: ", article['date_publish'])


                    try:
                        year = article['date_publish'].year
                        month = article['date_publish'].month
                        if category in ['Opinion', 'OP-ED', 'Editorial']:
                            article['primary_location'] = "LBR"
                            colname = f'opinion-articles-{year}-{month}'
                        else:
                            colname = f'articles-{year}-{month}'
                        #print(article)
                    except:
                        colname = 'articles-nodate'
                    print("Collection: ", colname)
                    try:
                        #TEMP: deleting the stuff i included with the wrong domain:
                        #myquery = { "url": final_url, "source_domain" : 'web.archive.org'}
                        #db[colname].delete_one(myquery)
                        # Inserting article into the db:
                        # db[colname].delete_one({"url" : url})
                        db[colname].insert_one(article)
                        # count:
                        if colname != 'articles-nodate':
                            url_count = url_count + 1
                            print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        else:
                            print("Inserted! in ", colname)
                        db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        # db[colname].delete_one({"url" : url})
                        # db[colname].insert_one(article)

                        print("DUPLICATE! Updated.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
                processed_url_count += 1
                print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

            else:
                pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
