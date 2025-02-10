# Packages:

import re
from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
import pandas as pd
from pymongo import MongoClient
from urllib.parse import urlparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from pymongo.errors import CursorNotFound
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

text = """
"""

direct_URLs = text.split('\n')
direct_URLs = [i for i in direct_URLs if "https://www.jamhurimedia.co.tz" in i]

source = 'jamhurimedia.co.tz'

hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


final_result = list(set(direct_URLs))   
print('Total number of urls found: ', len(final_result))



url_count = 0
processed_url_count = 0

for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}

            response = requests.get(url, headers=hdr)
            # process
            soup = BeautifulSoup(response.content)

            article = NewsPlease.from_html(response.text, url=url).__dict__

            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            article['language'] = 'sw'
            # title has no problem
            # print(soup)
          
            print("newsplease title: ", article['title'])

            if not article['maintext']:
                try:
                    article['maintext'] = soup.find('div', {'class' : 'post-content'}).text.strip()
                    
                except:
                    maintext = ''
                    for i in soup.find('div', {'class' : 'post-content'}).find_all('p'):
                        try:
                            maintext += i.text
                        except:
                            pass
                    article['maintext'] =  maintext.strip()
            if "Na " in  article['maintext'][:4]:
                article['maintext'] = "\n".join(article['maintext'].split('\n')[1:])
                
            if article['maintext']:
                print("newsplease maintext: ", article['maintext'][:50])
            
            try:
                date = soup.find('div', {'class' : 'post-date'}).text
                article['date_publish'] = dateparser.parse(date)
            except:
                article['date_publish'] =article['date_publish'] 
            print("newsplease date: ",  article['date_publish'])



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
