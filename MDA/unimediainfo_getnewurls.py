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
import pandas as pd

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


base = 'https://unimedia.info/ro/arhiva/'

source = 'unimedia.info'
source_domain = ['unimedia.info']

url_count = 0
processed_url_count = 0
total_final_result = 0

for year in range(2024, 2025):

    for month in range(10, 13):

        direct_URLs = []
        if month <10:
            strmonth = '0' + str(month)
        else:
            strmonth = str(month)

        for day in range(1, 27):
            if day < 10:
                strday = '0' + str(day)
            else:
                strday = str(day)

            url = base + str(year) + '/' + strmonth +'/' + strday
            print(url)

            reqs = requests.get(url, headers=headers)
            soup = BeautifulSoup(reqs.text, 'html.parser')
            try:
                for div in soup.find('div', {'id' : 'filterContainer'}).find_all('div', {'class' : 'col-xs-7'} ):
                    direct_URLs.append(div.find('a')['href'])
                print("Now collected", len(direct_URLs), "articles...")
            except:
                pass



        final_result = direct_URLs.copy()
        print(len(final_result))
        total_final_result += len(final_result)

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
                    # title has no problem
                
                    soup = BeautifulSoup(response.content, 'html.parser')
                    # blacklist by category:
                    try:
                        category = soup.find('meta', {'name' : 'article:section'})['content']
                    except:
                        category = 'News'
                    
                    if category in ['Sport', 'Shok!', 'Cultură/Turism', 'Auto', 'Youtube & FB', 'Tech/Media']:
                        article['date_publish'] = None
                        article['maintext'] = None
                        article['title'] ='From uninterested category'
                        print( article['title'], category)
                    else:
                        try:
                            date = soup.find('time', {'class' : 'timeago'})['datetime']
                            article['date_publish'] = dateparser.parse(date)
                        except:
                            article['date_publish'] = article['date_publish'] 
                        print("newsplease date: ", article['date_publish'])
                        print("newsplease title: ", article['title'])
                        print("newsplease maintext: ", article['maintext'][:50])
                

        #             
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
                        db[colname].delete_one({'url' : url, 'source_domain' : source})
                        db[colname].insert_one(article)
                        print("DUPLICATE! Updated.")
                        pass
                        
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
            else:
                pass
            processed_url_count += 1
                            
            print('\n',processed_url_count, '/', total_final_result, 'articles have been processed ...\n')
        time.sleep(5)
                            
        print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
