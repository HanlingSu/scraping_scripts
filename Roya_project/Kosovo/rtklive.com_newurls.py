#  Packages:
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

source = 'rtklive.com'

start = 402100
end = 640536
len_final_result = end - start
processed_url_count = 0
url_count = 0


for i in range(start, end):
    url = 'https://www.rtklive.com/sq/news-single.php?ID=' + str(i)
    print(url)
    hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    
    try:
        req = requests.get(url, headers = hdr)
        soup = BeautifulSoup(req.content)

        article = NewsPlease.from_html(req.text, url=url).__dict__
        # add on some extras
        article['date_download']=datetime.now()
        article['download_via'] = "Direct2"
        article['source_domain'] = source

        try:
            category = soup.find('span', {'class' : 'post-cat'}).text.strip()
        except:
            category = 'News'

        if category not in [ 'News', 'Bota', 'Rajoni dhe Bota', 'Lajme', 'Ekonomi', 'Kosovë', 'Shqipëri', 'Kronika', 'Gjykata Speciale']:
            article['maintext'] =  None
            article['date_publish'] = None
            article['title'] = 'From uninterested category'
            print(article['title'], category)
        else:
            
            try:
                maintext = ''
                for i in soup.find('div', {'class' : 'post-content'}).find_all('p'):
                    maintext += i.text 
                article['maintext'] = maintext.strip()
            except:
                maintext = soup.find('div', {'class' : 'post-content'}).text
                article['maintext'] = maintext.strip()

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


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")

