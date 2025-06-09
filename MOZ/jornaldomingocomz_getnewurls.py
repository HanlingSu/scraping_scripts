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
import json
# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []
source = 'jornaldomingo.co.mz'

sitemap_base = 'https://www.jornaldomingo.co.mz/post-sitemap'

for i in range(20, 22):
    sitemap = sitemap_base + str(i) + '.xml'
    print(sitemap)
    hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
    req = requests.get(sitemap, headers = hdr)
    soup = BeautifulSoup(req.content)
    item = soup.find_all('loc')

    for i in item:
        direct_URLs.append(i.text)


    print('Now scraped ', len(direct_URLs), ' articles from previous pages.')

##############################################################################################

# # category
# base = 'https://www.jornaldomingo.co.mz/category/'
# page_start = [1, 1, 1, 1, 1, 1]
# page_end = [520, 140, 86, 120, 70, 90]

# category = ['nacional', 'politica', 'economia', 'sociedade', 'internacional', 'em-foco']

# for c, ps, pe in zip(category, page_start, page_end):
#     for p in range(ps, pe+1):
#         url = base + c + '/page/' + str(p)
#         print(url)
#         hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
#         req = requests.get(url, headers = hdr)
#         soup = BeautifulSoup(req.content)
#         item = soup.find_all('h2', {'class' : 'post-title' })
#         for i in item:
#             direct_URLs.append(i.find('a')['href'])
#         print('Now scraped ', len(direct_URLs), ' articles from previous pages.')

# final_result = direct_URLs.copy()[::-1]
# print(len(final_result))
##############################################################################################


blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

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
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            response = requests.get(url, headers=header)
            # process
            article = NewsPlease.from_html(response.text, url=url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            # title date and main text has no problem  

          
            print("newsplease date: ", article['date_publish'])
            print("newsplease title: ", article['title'])

            try:
                maintext = ''
                for i in soup.find('div', {'class' : 'entry-content entry clearfix'}).find_all('p'):
                    if not i.find('strong'):
                        maintext += i.text
            except:
                maintext = article['maintext']
            article['maintext'] = maintext

            print("newsplease maintext: ", article['maintext'][:50])
         
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'articles-{year}-{month}'
                
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
                print("DUPLICATE! Update.")
                
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')
    
    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
