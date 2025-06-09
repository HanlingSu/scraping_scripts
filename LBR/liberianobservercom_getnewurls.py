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

source = 'liberianobserver.com'

direct_URLs = []
# base = 'https://www.liberianobserver.com/article/sitemap.xml?page='
base = "https://www.liberianobserver.com/search/?tncms_csrf_token=916d675b61d57da2bb15377bbe4b13df12c51605c665d1f10aca1c87239b953a.ce3573bdd7f5881a5b5e&d1=2025-01-01&d2=2025-04-17&sd=desc&l=10&nsa=eedition&q=+&app%5B0%5D=editorial&o="
for p in range(0, 210):
    url = base+str(p*10)
    print(url)
    req = requests.get(url, headers = headers)
    soup = BeautifulSoup(req.content)

    for i in soup.find_all('h3', {'class'  : 'tnt-headline'}):
        direct_URLs.append(i.find('a')['href'])
    print(len(direct_URLs))

direct_URLs = ['https://www.liberianobserver.com' + i for i in direct_URLs]

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
                category = soup.find('ol', {'class' : 'breadcrumb'}).find_all('li')[1].text.strip()
            except:
                category = 'News'

            if category in ['Business', 'Sports', 'Opinion', 'Lib Life', 'Obituaries']:
                article['maintext'] = None
                article['date_publish'] = None
                article['title'] = 'From uninterested category!'
                print(article['title'], category)
            else:
                print("newsplease title: ", article['title'])
                # Get Main Text:
                try:
                    soup.find('div', {'id': 'article-body'}).find_all('p')
                    maintext = ''
                    for i in soup.find('div', {'id': 'article-body'}).find_all('p'):
                        maintext += i.text
                    article['maintext'] = maintext.strip()
                except:
                    try:
                        maintext = soup.find('div', {'id': 'article-body'}).text
                        article['maintext'] = maintext.strip()
                    except:
                        maintext = article['maintext'] 
                        article['maintext']  = maintext.strip()       
            
                print("newsplease maintext: ", article['maintext'][:50])
                
                # date
                try:
                    date = soup.find("meta", {"itemprop":"datePublished"})['content']
                    article['date_publish'] = dateparser.parse(date).replace(tzinfo = None)
                except:
                    date = soup.find('time', {'class' : 'tnt-date asset-date text-muted'})['datetime']
                    article['date_publish'] = dateparser.parse(date).replace(tzinfo = None)
                print("newsplease date: ", article['date_publish'])


            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
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
                db[colname].delete_one({"url" : url})
                db[colname].insert_one(article)

                print("DUPLICATE! Updated.")
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
