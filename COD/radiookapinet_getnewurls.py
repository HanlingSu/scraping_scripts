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

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
direct_URLs = []

source = 'radiookapi.net'

# for i in range(158, 160):
#     base_link = 'https://www.radiookapi.net/sitemap.xml?page=' + str(i)
#     hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
#     req = requests.get(base_link, headers = hdr)
#     soup = BeautifulSoup(req.content)
#     item = soup.find_all('loc')
#     for j in item:
#         if '/2024' in j.text:
#             direct_URLs.append(j.text)
#     print('Now scraped ', len(direct_URLs), ' articles from previous pages.')



# 150

for p in range(2, 170):
    url = 'https://www.radiookapi.net/actualite?page=' + str(p)
    hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
    req = requests.get(url, headers = hdr)
    soup = BeautifulSoup(req.content)
    item = soup.find_all('h2', {'class' : 'field-content'})
    for j in item:
        # if '/2024' in j.text:
            direct_URLs.append(j.find('a')['href'])
    print('Now scraped ', len(direct_URLs), ' articles from previous pages.')


blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

final_result = list(set(direct_URLs))
final_result = ['https://www.radiookapi.net' + i for i in final_result]
print('Total number of urls found: ', len(final_result))


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
            # title has no problem
            print("newsplease title: ", article['title'])
           
            print("newsplease maintext: ", article['maintext'][:50])
            print("newsplease date: ", article['date_publish'])
            
            
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'articles-{year}-{month}'
                
            except:
                colname = 'articles-nodate'
            
            # Inserti ng article into the db:
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
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
