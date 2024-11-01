# Packages:
import os
import re
import pandas as pd
import numpy as np 

from pymongo import MongoClient


import bs4
from bs4 import BeautifulSoup
from dateparser.search import search_dates
import dateparser
import requests
from urllib.parse import quote_plus

from pymongo import MongoClient
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p



headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

source = 'elcomercio.com'

base = 'https://www.elcomercio.com/categoria/opinion/editorial/page/'
for i in range(2, 5):
    direct_URLs = []

    url = base+str(i)
    reqs = requests.get(url, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    for j in soup.find_all('h3'):
        direct_URLs.append(j.find('a')['href'])
    print(len(direct_URLs))


    direct_URLs = [ i for i in direct_URLs if "/opinion" in i]

    final_result = list(set(direct_URLs))
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
                print("newsplease date: ", article['date_publish'])
                print("newsplease title: ", article['title'])


            
                soup = BeautifulSoup(response.content, 'html.parser')

                # Get Main Text:
                try:
                    soup.find('div', {'class': 'entry__content'}).find_all('p')
                    maintext = ''
                    for i in soup.find('div', {'class': 'entry__content'}).find_all('p'):
                        maintext += i.text
                    article['maintext'] = maintext
                except:
                    try:
                        maintext = soup.find('div', {'class': 'entry__content'}).text
                        article['maintext'] = maintext
                    except:
                        try:
                            soup.find('div', {'class': 'entry__content tbl-forkorts-article tbl-forkorts-article-active'}).find_all('p')
                            maintext = ''
                            for i in soup.find('div', {'class': 'entry__content tbl-forkorts-article tbl-forkorts-article-active'}).find_all('p'):
                                maintext += i.text
                            article['maintext'] = maintext
                        except:
                            maintext = article['maintext'] 
                            article['maintext']  = maintext       
            
                print("newsplease maintext: ", article['maintext'][:50])
                

                try:
                    year = article['date_publish'].year
                    month = article['date_publish'].month
                    colname = f'opinion-articles-{year}-{month}'
                    article['primary_location'] = "ECU"
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
                    print("DUPLICATE! PASS.")
            except Exception as err: 
                print("ERRORRRR......", err)
                pass
            processed_url_count += 1
            print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

        else:
            pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
