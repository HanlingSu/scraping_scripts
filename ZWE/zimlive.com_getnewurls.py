# Packages:
from pymongo import MongoClient

from bs4 import BeautifulSoup
from newspaper import Article
import requests

from pymongo import MongoClient
from datetime import datetime
from pymongo.errors import DuplicateKeyError
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
import json
import dateparser
import time

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

source = 'zimlive.com'

direct_URLs = []

for i in range(10, 12):
    sitemap = 'https://www.zimlive.com/post-sitemap' + str(i) + '.xml' 
    print(sitemap)
    reqs = requests.get(sitemap, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    for link in soup.find_all('loc'):
        direct_URLs.append(link.text)

    print(len(direct_URLs))



final_result = direct_URLs.copy()

url_count = 0
processed_url_count = 0
for url in final_result[::-1]:
    if url:
        print(url, "FINE")
        time.sleep(1)
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

            soup = BeautifulSoup(response.content, 'html.parser')
            time.sleep(1)
            try:
                category = soup.find('nav', {'class' : 'breadcrumbs'}).text.strip().split(' » ')
            except:
                category = 'News'

            if any(c in category for c in ['Life & Style', 'Travel', 'Sport', 'Football', 'Showbiz', 'Events Guide', 'Arts & Culture']):
                print('From uninterested category')
            else:


                print("newsplease date: ", article['date_publish'])

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
                    myquery = { "url": url}
                    db[colname].delete_one(myquery)
                    db[colname].insert_one(article)
                    print("DUPLICATE! Updated.")
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")