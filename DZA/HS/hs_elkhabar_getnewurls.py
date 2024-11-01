
# Packages:
import time
import random
import sys
sys.path.append('../')
import os
import re
from p_tqdm import p_umap
from tqdm import tqdm
from pymongo import MongoClient
import random
from urllib.parse import urlparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from pymongo.errors import CursorNotFound
import requests
#from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from dotenv import load_dotenv
from bs4 import BeautifulSoup
# %pip install dateparser
import dateparser
import pandas as pd

# db connection:
uri = 'mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true'
db = MongoClient(uri).ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## NEED TO DEFINE SOURCE!
source = 'elkhabar.com'

direct_URLs = []
for year in range(2024, 2025):
    yearstr = str(year)

    for month in range(6, 9) :
        

        if month < 10:
            monthstr = '0' +str(month)
        else:
            monthstr = str(month)

        for day in range(1, 32):
            if day < 10:
                daystr = '0' + str(day)
            else:
                daystr = str(day)

            for p in range(1,10):

                url = "https://www.elkhabar.com/archive/?csrfmiddlewaretoken=dto1Qe8Ci8oer5PcYfjVH9AaSmTRz8lb&date_archive=" + yearstr + '-' +monthstr +'-' +daystr + "&page=" + str(p)
                
                time.sleep(2)

                reqs = requests.get(url, headers=headers)
                soup = BeautifulSoup(reqs.text, 'html.parser')

                for link in soup.find_all('h3', {'class' :'panel-title'}):
                    direct_URLs.append(link.find('a')['href']) 

            print(yearstr + '-' +monthstr +'-' +daystr, len(direct_URLs))
        print("Number of urls so far: ", len(direct_URLs))

        # STEP 2: Get rid or urls from blacklisted sources + DUPLICATES
        dedup_urls = list(set(direct_URLs))

        final_result = ['https://www.elkhabar.com' + i for i in dedup_urls if "https://www.elkhabar.com" not in i ]
        
        print("Total number of USABLE urls found: ", len(final_result))
        time.sleep(2)

        ## INSERTING IN THE DB:
        url_count = 0
        processed_url_count = 0

        for url in final_result:
            if url == "":
                pass
            else:
                if url == None:
                    pass
                else:
                    if "elkhabar.com" in url:
                        print(url)
                        ## SCRAPING USING NEWSPLEASE:
                        try:
                            # count:
                            url_count = url_count + 1
                            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
                            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                            response = requests.get(url, headers=header)
                            soup = BeautifulSoup(response.content, 'html.parser')
                            article = NewsPlease.from_html(response.text, url=url).__dict__

                            # add on some extras
                            article['date_download']=datetime.now()
                            article['download_via'] = "Direct2"
                            article['source_domain'] = source
                            article['language'] = 'ar'
                            
                            if not article['maintext']:
                                try:
                                    maintext = ''
                                    for i in soup.find('div', {'id' : 'article_body_content'}).find_all('p'):
                                        maintext += i.text
                                    article['maintext'] = maintext.strip()
                                except:
                                    maintext = soup.find('div', {'id' : 'article_body_content'}).text
                                    article['maintext'] = maintext.strip()
                
                            ## Inserting into the db
                            try:
                                year = article['date_publish'].year
                                month = article['date_publish'].month
                                colname = f'articles-{year}-{month}'
                                #print(article)
                            except:
                                colname = 'articles-nodate'

                            try:

                                # Inserting article into the db:
                                db[colname].insert_one(article)
                                print("DATE: ",article['date_publish'], " - Month: ",article['date_publish'].month)
                                print("TITLE: ",article['title'])
                                print("MAIN TEXT: ",article['maintext'][0:50])
                                print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                            except DuplicateKeyError:
                                db[colname].delete_one({'url' : url})
                                db[colname].insert_one(article)
                                print("DUPLICATE! Updated." )
                        except Exception as err: 
                            print("ERRORRRR......", err)
                            #pass
                        processed_url_count += 1
                        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')
                    else:
                        print("++ nothing: ", url)
                        
        print("Done inserting ", url_count, " manually collected urls from ",  source, " ", yearstr, "-", monthstr)
        time.sleep(2)

