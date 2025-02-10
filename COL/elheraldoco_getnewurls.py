
# Packages:
from typing import final
from unicodedata import category
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import dateparser
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import re
import pandas as pd

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
direct_URLs = []
source = 'elheraldo.co'

# categories= ['local', 'region', 'judicial', 'internacional', 'politica', 'nacional', 'coronavirus', 'economia']
# pages_start = [1, 1, 1, 1, 1, 1,1,1]
# # pages_end = [80,20,100,0,0,0,0,0]
# pages_end = [70,  10, 90, 110, 35, 230, 5, 60 ]

# for c, ps, pe in zip(categories,pages_start, pages_end):
#     for i in range(ps, pe+1):
#         link = 'https://www.elheraldo.co/' + c + '?page=' + str(i)
#         hdr = {'User-Agent': 'Mozilla/5.0'}
#         req = requests.get(link, headers = hdr)
#         soup = BeautifulSoup(req.content)
#         items = soup.find_all('article', {'class' : 'item foto-titulo'})
#         for item in items:
#             direct_URLs.append(item.find('div', {'class' : 'text'}).find('h1').find('a')['href'])
#         direct_URLs = list(set(direct_URLs))    
#         print('Now collected ', len(direct_URLs), 'articles from previous pages...')

# direct_URLs = ['https://www.elheraldo.co' + i for i  in direct_URLs]

direct_URLs = pd.read_csv('/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/COL/elheraldoco.csv')['0']

blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

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
            print("newsplease title: ", article['title'])
            print("newsplease maintext: ", article['maintext'][:50])
 
            ## Fixing Date:
            soup = BeautifulSoup(response.content, 'html.parser')
            try:
                date = soup.find('meta', {'property' : 'article:published_time'})['content']
                article['date_publish'] = dateparser.parse(date)
            except:
                article['date_publish'] = article['date_publish'] 
            print("newsplease date: ", article['date_publish'])
            
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
