
from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from random import randint, randrange
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import langid
import cloudscraper
import re

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []
source = 'elviajero.com.do'
header ={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'} #header settings

base = 'https://www.elviajero.com.do/category/opiniones/page/'
for p in range(0, 42):
    url = base+str(p)

    reqs = requests.get(url, headers=header)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    for link in soup.find('div', {'class' : 'aft-archive-wrapper'}).findAll('div', {'class':'read-title'}):
            direct_URLs.append(link.find('a')['href'])
    print("Urls so far: ",len(direct_URLs))




final_result = direct_URLs.copy()[::-1]
print(len(final_result))

url_count = 0
processed_url_count = 0

for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            response = requests.get(url, headers=header)
            # process
            article = NewsPlease.from_html(response.text, url=url).__dict__

            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            article['url'] = url

            soup = BeautifulSoup(response.content)

            # category
            try:
                category = soup.find('li', {'class' : 'meta-category'}).text.strip()
            except:
                category = "news"

            if category in ['Deportes', 'Diversion']:
                pass
            else:
                # title has no problem
                print("newsplease title: ", article['title'])
                print("newsplease date: ",  article['date_publish'])
                if 'por' in article['maintext'][:5].lower():
                    article['maintext'] = '\n'.join(article['maintext'].split('\n')[1:])
                print("newsplease maintext: ", article['maintext'][:50])
                
                try:
                    year = article['date_publish'].year
                    month = article['date_publish'].month
                    colname = f'opinion-articles-{year}-{month}'
                    article['primary_location'] = "DOM"
                    
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
                    # myquery = { "url": url, "source_domain" : source}
                    # db[colname].delete_one(myquery)
                    # db[colname].insert_one(article)
                    print("DUPLICATE! Pass.")
                    pass
                
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')
    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")