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
# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'prishtinainsight.com'

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


base = 'https://prishtinainsight.com/post-sitemap'


direct_URLs = []


for i in range(4, 4+1):
    link = base + str(i)+ '.xml'
    print(link)
    reqs = requests.get(link, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    for i in soup.find_all('loc'):
        direct_URLs.append(i.text)
    
    print(len(direct_URLs))


final_result = direct_URLs.copy()[::-1]

print(len(final_result))


processed_url_count = 0
url_count = 0
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
            
            print('newsplease date: ', article['date_publish'])
            print("newsplease title: ", article['title'])

           
            soup = BeautifulSoup(response.content, 'html.parser')
        
            try:
                maintext = ''
                for p in soup.find('div', {'class' : 'singleContent'}).find_all('p'):
                    maintext += p.text
                article['maintext'] = maintext.strip()
            except:
                try:
                    article['maintext'] = soup.find('div', {'class' : 'singleContent'}).text.strip()
                except:
                    article['maintext'] = article['maintext'] 
            print("newsplease maintext: ", article['maintext'][:50])
            
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
                db[colname].insert_one(article)
                # count:
                if colname != 'articles-nodate':
                    url_count = url_count + 1
                    print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                else:
                    print("Inserted! in ", colname)
                db['urls'].insert_one({'url': article['url']})
            except DuplicateKeyError:
                print("DUPLICATE! Not inserted.")
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')
        if processed_url_count % 7== 0 :
            time.sleep(60)
    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
