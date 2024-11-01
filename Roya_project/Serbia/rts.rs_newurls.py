# Packages:
import re
from pymongo import MongoClient
from bs4 import BeautifulSoup
from newspaper import Article
from dateparser.search import search_dates
import dateparser
import requests

from pymongo import MongoClient
from datetime import datetime
from pymongo.errors import DuplicateKeyError
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from dotenv import load_dotenv

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

source = 'rts.rs'

direct_URLs = []


category = ['politika', 'region', 'svet', 'ratu-u-ukrajini', 'drustvo', 'ekonomija']

page_start = [1,1,1,1,1,1]
# page_end = [1,1,1,1,1,1]

page_end = [970, 520, 1010, 114, 1600, 395]
for c, ps, pe in zip(category, page_start, page_end):
    for p in range(ps, pe+1):
        url = 'https://www.rts.rs/vesti/' + c + '.html?position=' + str(p)
        print(url)
        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')
        for link in soup.find_all('h3'):
            direct_URLs.append(link.find('a')['href'])
        print('Now collected', len(direct_URLs), 'articles ...')


direct_URLs = ['https://www.rts.rs' + i for i in direct_URLs ]

final_result = direct_URLs.copy()

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

            try:
                maintext = soup.find("div", {'id' : 'story-text'}).text.strip()
                article['maintext'] = maintext
            except:
                maintext = soup.find("p", {'class' : 'lead storyMainLead'}).text.strip()
                article['maintext'] = maintext

            print("newsplease maintext: ", article['maintext'][:50])                    
            
            
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'articles-{year}-{month}'
                #print(article)
            except:
                colname = 'articles-nodate'
            #print("Collection: ", colname)
            try:
                #TEMP: deleting the stuff i included with the wrong domain:
                #myquery = { "url": final_url, "source_domain" : 'web.archive.org'}
                #db[colname].delete_one(myquery)
                # Inserting article into the db:
                db[colname].insert_one(article)
                # count:
                url_count = url_count + 1
                print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                db['urls'].insert_one({'url': article['url']})
            except DuplicateKeyError:
                print("DUPLICATE! Not inserted.")
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
