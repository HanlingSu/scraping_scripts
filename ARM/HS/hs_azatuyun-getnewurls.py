

import requests
import io as io
from io import StringIO ## for Python 3
# Packages:
import random
import sys
sys.path.append('../')
import os
import re
#from p_tqdm import p_umap
#from tqdm import tqdm
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
#from dotenv import load_dotenv
from bs4 import BeautifulSoup
# %pip install dateparser
import dateparser
import pandas as pd


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'azatutyun.am'

### EXTRACTING ulrs from sitemaps:
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# category = ['news', 'z/2039', 'z/2095', 'z/2041', 'z/2040', 'z/2038', 'z/2081', 'z/2037']
#                     # political, right, economics, society, karabakh problem, international, region
# page_start = [1, 1, 1, 1, 1, 1, 1, 1 ]
# page_end = [100, 10, 10, 1, 10, 10, 12, 10]  

# direct_URLs = []
# for c, ps, pe in zip(category, page_start, page_end):
#     for p in range(ps, pe+1):
#         url = 'https://www.azatutyun.am/' + c +'?p=' + str(p)
#         reqs = requests.get(url, headers=headers)
#         soup = BeautifulSoup(reqs.text, 'html.parser')

#         for i  in soup.find_all('li', {'class' :'col-xs-12 col-sm-12 col-md-12 col-lg-12 fui-grid__inner'}):
#             direct_URLs.append(i.find('a')['href'])
#         print('Now collected', len(direct_URLs), 'URLs ... ')
# direct_URLs = list(set(direct_URLs))

# direct_URLs = ['https://www.azatutyun.am' + i for i in direct_URLs]
url_count = 0
processed_url_count = 0
for i in range(33254507,  33353901):
    url = 'https://www.azatutyun.am/a/'+ str(i) + '.html'

# final_result = direct_URLs.copy()



# for url in final_result:
    ## INSERTING IN THE DB:
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
        # article['language'] = 'hy'
        
        ## Fixing what needs to be fixed:
        soup = BeautifulSoup(response.content, 'html.parser')
        article['url'] = soup.find('meta', {'property' : 'og:url'})['content']
        print(article['url'])

        # Get Title:
        try:
            contains_title = soup.find("meta", {"name":"title"})
            title = contains_title['content']
            article['title'] = title
        except:
            try:
                title = soup.find("title").text
                article['title'] = title
            except:
                article['title'] = article['title']

        print('Title: ', article['title'])


        # Get Main Text:
        if article['maintext'] == None:
            try:
                maintext = soup.find("div", {"class":"wsw"}).text
                article['maintext'] = maintext
            except:
                try:
                    contains_maintext = soup.find("meta", {"name":"description"})
                    maintext = contains_maintext['content']
                    article['maintext'] = maintext  
                except: 
                    maintext = None
                    article['maintext']  = None

        print('Maintext: ', article['maintext'][:50])

        
        ## Fixing Date:
        try:
            contains_date = soup.find("time")['datetime']
            article_date = dateparser.parse(contains_date)
            article['date_publish'] = article_date
        except:
            article['date_publish'] = article['date_publish'] 
            
        print('Date: ', article['date_publish'])
        ## Inserting into the db
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
            db[colname].delete_one({'url' : url})
            db[colname].insert_one(article)
            pass
            print("DUPLICATE! Updated.")
            
    except Exception as err: 
        print("ERRORRRR......", err)
        pass
    processed_url_count += 1
    # print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

else:
    pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")

