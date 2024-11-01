
# Packages:
from typing import final
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import dateparser
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import re
import time

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'adaderana.lk'

base = 'http://www.adaderana.lk/hot-news/?pageno='

# 5002
for p in range(47, 60):
  
    direct_URLs = []
    link = base + str(p)
    hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    
    req = requests.get(link, headers = hdr)
    soup = BeautifulSoup(req.content)
    items = soup.find_all('div', {'class' : 'news-story'})
    for i in items:
        direct_URLs.append(i.find('h2').find('a')['href'])
    # time.sleep(1)
    print(len(direct_URLs))
    # print(soup)

    final_result = list(set(direct_URLs))
    print(len(final_result))

    url_count = 0
    processed_url_count = 0
    for url in final_result:
        if url:
            # time.sleep(60)
            print(url, "FINE")
            print('now scraping', str(p))
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
                # print("newsplease date: ", article['date_publish'])
                print("newsplease title: ", article['title'])
                print("newsplease maintext: ", article['maintext'][:50])
    
                ## Fixing Date:
                soup = BeautifulSoup(response.content, 'html.parser')

                try:
                    date = soup.find('p', {'class' : 'news-datestamp'}).text
                    article['date_publish'] = dateparser.parse(date)
                except:
                    article['date_publish'] = None
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
                    if colname !=  'articles-nodate':
                        db[colname].insert_one(article)
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
    time.sleep(600)

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
