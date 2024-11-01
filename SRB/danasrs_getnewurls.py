# Packages:
from re import escape
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
import json
import re

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# collect direct URLs
# direct_URLs = []
# sitemap_base = 'https://www.danas.rs/post-sitemap'

# for i in range(1, 105):
#     sitemap = sitemap_base + str(i) + '.xml'
#     print('Scraping from ', sitemap, ' ...')

#     hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
#     req = requests.get(sitemap, headers = hdr)
#     soup = BeautifulSoup(req.content)
#     item = soup.find_all('loc')

#     for i in item:
#         direct_URLs.append(i.text)
    
#     print('Now scraped ', len(direct_URLs), ' articles from previous sitemaps.')

direct_URLs = []
source = 'danas.rs'

#sitemap_base = 'https://www.danas.rs/sitemap-pt-post-2022-'

sitemap_base = 'https://www.danas.rs/sitemap-pt-post-p'

#https://www.danas.rs/sitemap-pt-post-p4-2022-03.xml

# for month in range(9, 13): # These are months!
#     if month <10:
#         str_month = '0' + str(month)
#     else:
#         str_month = str(month)

#     for j in range(1, 11):
#         sitemap = sitemap_base + str(j) + '-2023-' + str_month + '.xml'
#         print('NOW SCRAPING ', sitemap, ' ... ')
#         hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
#         req = requests.get(sitemap, headers = hdr)
#         soup = BeautifulSoup(req.content)
#         item = soup.find_all('loc')
            
#         for i in item:
#             direct_URLs.append(i.text)   
            
#     print('Now scraped ', len(direct_URLs), ' articles from previous sitemaps.')

for p in range(1, 1150+1):
    url = 'https://www.danas.rs/najnovije-vesti/page/' + str(p)
    hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
    req = requests.get(url, headers = hdr)
    soup = BeautifulSoup(req.content)
    item = soup.find_all('h3', {'class' : 'article-post-title'})
        
    for i in item:
        direct_URLs.append(i.find('a')['href'])   
        
    print('Now scraped ', len(direct_URLs), ' articles from previous pages.')


blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

final_result = direct_URLs.copy()
print('Total number of urls found: ', len(final_result))



# custom parser and insert article into DB
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

            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # fix maintext
            try:
                soup.find('div', {'class' : 'post-content content'}).find_all('p')
                maintext = ''
                for i in soup.find('div', {'class' : 'post-content content'}).find_all('p'):
                    maintext += i.text.strip()
                article['maintext'] = maintext
            except:
                article['maintext'] = article['maintext'] 
                
            if article['maintext']:
                print("newsplease maintext: ", article['maintext'][:50])
                
            # fix date
            try:
                date = json.loads(soup.find('script', type='application/ld+json').string, strict=False)['datePublished']
                article['date_publish'] = dateparser.parse(date).replace(tzinfo= None)
            except:
                try:
                    date = soup.find('span', {'class' : 'post-meta post-date'}).text
                    article['date_publish'] = dateparser.parse(date, settings = {'DATE_ORDER' : 'DMY'})
                except:
                    article['date_publish'] = article['date_publish']
            
            if  article['date_publish']:
                print("newsplease date: ",  article['date_publish'])
      
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
