# Packages:
from pymongo import MongoClient
from bs4 import BeautifulSoup
from newspaper import Article
from dateparser.search import search_dates
import requests
from pymongo import MongoClient
from urllib.parse import urlparse
from datetime import datetime
from pymongo.errors import DuplicateKeyError
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from dotenv import load_dotenv
import re
import pandas as pd

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []
# base = 'https://www.kbc.co.ke/post-sitemap'
source = 'kbc.co.ke'

# direct_URLs = pd.read_csv('/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/KEN/kbccoke.csv')['0']
# for i in range(1, 2):
#     sitemap = base + str(i) + '.xml'
#     print(sitemap)
#     hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
#     req = requests.get(sitemap, headers = hdr)
#     soup = BeautifulSoup(req.content)
#     item = soup.find_all('a')

#     for i in item:
#         direct_URLs.append(i['href'])


#     print('Now scraped ', len(direct_URLs), ' articles from previous sitemaps.')

base = 'https://www.kbc.co.ke/category/news/page/'
for p in range(1, 3):
    url = base + str(p)
    print(url)
    hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
    req = requests.get(url, headers = hdr)
    soup = BeautifulSoup(req.content)

    for i in soup.find('div', {'class' :'td-ss-main-content'}).find_all('h3', {'class' : 'entry-title td-module-title'}):
        direct_URLs.append(i.find('a')['href'])
    print(len(direct_URLs))


blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

final_result = direct_URLs.copy()
print(len(final_result))

url_count = 0
processed_url_count = 0

for url in final_result:
    # if url:
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
        

        response = requests.get(url, headers=header)

        soup = BeautifulSoup(response.content, 'html.parser')

        try:
            category = soup.find('li', {'class' : 'entry-category'}).text
        except:
            category = 'News'
        
        if category in ['Celebrity', 'Entertainment', 'Lifestyle', 'Business', 'Sports', 'Podcasts', 'Technology', 'Markets', 'Athletics']:
            article['date_publish'] = None
            article['maintext'] = None
            article['title'] = 'From uninterested category!'
            print(article['title'], category)
        else:
            print("newsplease date: ", article['date_publish'])
            print("newsplease title: ", article['title'])
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
                pass
                print("DUPLICATE! Not inserted.")
            
    except Exception as err: 
        print("ERRORRRR......", err)
        pass
    processed_url_count += 1
    print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

    # else:
    #     pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
