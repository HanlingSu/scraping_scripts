
"""
Created on Oct 26, 2022 

Craated by Hanling Su
"""

# Packages:

from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from datetime import datetime
from pymongo.errors import DuplicateKeyError
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
import re

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p



base = 'https://www.thediliweekly.com/category/'
source = 'thediliweekly.com'

category = ['notisias', 'editorial1', 'kapital', 'english-page', 'dezenvolvimentu', 'saude', 'seguransadefeza', 'jender', 'labarikjoventude', 'direitos-humanos']
page_start =  [1] * len(category)
page_end = [3] * len(category)


for ps, pe, c in zip(page_start, page_end, category):
    direct_URLs = []
    for p in range(ps, pe+1):
        link = base + c + '?start=' + str(p) 
        print(link)
        hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        req = requests.get(link, headers = hdr)
        soup = BeautifulSoup(req.content)
        try:
            for h3 in soup.find_all('h3', {'class' : 'entry-title td-module-title'}):
                direct_URLs.append(h3.find('a')['href'])
        except:
            pass
        print(len(direct_URLs))

    # direct_URLs = ['https://www.thediliweekly.com' + i for i in direct_URLs]
    final_result = direct_URLs.copy()

    print('Now have collected', len(final_result), 'articles from', c)


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
                
                print("newsplease title: ", article['title'])

               
                print("newsplease date: ", article['date_publish'])

                try:
                    maintext= soup.find('div', {'class' : 'td-post-content tagdiv-type'}).text
                    article['maintext'] = maintext.strip()
                    
                except:
                    maintext = ''
                    for i in soup.find('div', {'class' : 'td-post-content tagdiv-type'}).find_all('p'):
                        maintext += i.text
                    article['maintext'] = maintext.strip()
                print("newsplease maintext: ", article['maintext'][:50])

                try:
                    year = article['date_publish'].year
                    month = article['date_publish'].month
                    if "editorial1" in url:
                        colname = f'opinion-articles-{year}-{month}'
                        article['primary_location'] = 'TLS'
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
                    db[colname].delete_one({ "url": url, "source_domain" : source})
                    db[colname].insert_one(article)
                    
                    print("DUPLICATE! Updated.")
                    
            except Exception as err: 
                print("ERRORRRR......", err)
                pass
            processed_url_count += 1
            print('\nNow scraping ', c)
            print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

        else:
            pass

    print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
