
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

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}



base = 'https://elblog.com/category/'
direct_URLs = []

categories = ['noticias', 'internacionales', 'politica']
page_start = [1, 1, 1]
page_end = [2000, 500, 145]
# page_end = [4455, 911, 145]

for c, ps, pe in zip(categories, page_start, page_end):
    for p in range(ps, pe):
        url = base + c + '/page/' + str(p)
        print(url)
        reqs = requests.get(url, headers=header)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        for i in soup.find_all('div', {'class' : 'overflow-hidden relative0 md:mb-20 rounded-b-2xl shadow-2xl px-4 pt-0 pb-4 hover:-translate-y-2 transition-all'}):
            try:
                direct_URLs.append(i.find('a')['href'])
            except:
                pass

        print(len(direct_URLs))

final_result = list(set(direct_URLs))
print(len(final_result))

source = 'elblog.com'
url_count = 0
for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            response = requests.get(url, headers=header)
            # process
            article = NewsPlease.from_html(response.text, url=url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            article['mlp'] = False
           
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # fix maintext
         
            article['maintext']  = article['maintext'].split('\n', 2)[2]
            
            if  article['maintext']:
                print("newsplease maintext: ", article['maintext'][:50])
            
            # fix date
         
            print("newsplease date: ", article['date_publish'])
            
            # fix title
            print("newsplease title: ", article['title'])

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
                db[colname].delete_one({'url': article['url']})
                db[colname].insert_one(article)

                print("DUPLICATE! updated.")
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
