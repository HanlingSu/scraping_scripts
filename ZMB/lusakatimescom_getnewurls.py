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

source = 'lusakatimes.com'
direct_URLs = []

# # sitemap
# sitemap_base = 'https://www.lusakatimes.com/post-sitemap'

# for i in range(1, 2):
#     sitemap = sitemap_base + str(i) +'.xml'
#     # mundo, nacionales, noticias-del-dia, espectaculos, ciencia
#     hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
#     req = requests.get(sitemap, headers = hdr)
#     soup = BeautifulSoup(req.content)
#     item = soup.find_all('loc')
#     for i in item:
#         direct_URLs.append(i.text)

#     direct_URLs = direct_URLs
#     print(len(direct_URLs))

# category

base = 'https://www.lusakatimes.com/'
categories = ['other-news', 'zambiancolumn', 'economy','headlines', 'ruralnews']

page_start = [1, 1, 1, 1, 1]
page_end = [20, 12, 8, 18, 3]

direct_URLs = []


for c, ps, pe in zip(categories, page_start, page_end):
    for p in range(ps, pe+1):
        link = base + c + '/page/' + str(p) 
        # print(link)
        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
        req = requests.get(link, headers = hdr)
        soup = BeautifulSoup(req.content)
        item = soup.find_all('h3', {'class' : 'entry-title td-module-title'})
        for i in item:
            direct_URLs.append(i.find('a')['href'])
        print('Now scraped ', len(direct_URLs), ' articles from previous pages.')


blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

final_result = direct_URLs.copy()
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
            # title has no problem
            print("newsplease title: ", article['title'])
            print("newsplease maintext: ", article['maintext'][:50])
            print("newsplease date: ",  article['date_publish'])
            
            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser')
            try:
                category = soup.find('li', {'class' : 'entry-category'}).text.strip()
            except:
                category = 'News'

            print(category)

            if category in ['Sports', 'Entertainment News', 'Feature Lifestyle']:
                article['title'] = 'From uninterested categories!!'
                article['maintext'] = None
                article['date_publish'] = None
                print('\nFrom uninterested category:', category)
                
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
