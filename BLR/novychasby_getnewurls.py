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

# https://novychas.online/sitemap.xml.gz

source = 'novychas.by'
# # by scraping downloaded sitemaps
# with open('/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/BLR/novychas_sitemap.xml', 'r') as f:
#     data = f.read()
    
# Bs_data = BeautifulSoup(data, "xml")
# print(Bs_data)
# direct_URLs = []
# for i in Bs_data.find_all('loc'):
#     direct_URLs.append(i.text)
# print(len(direct_URLs))
# blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
# blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
# direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

# final_result = []
# print(len(direct_URLs))
# for i in direct_URLs:
#     if i.split('https://novychas.online/')[-1].split('/')[0] not in ['kultura', 'poviaz', 'asoba', 'sport', 'donate', 'blogs']: 
#         final_result.append(i)

# print('TOTAL LINKS:', len(final_result))
# final_result = final_result[-2000:]


# by scraping categorized news 
categories = ['zamezza', 'palityka', 'hramadstva', 'ekanomika']
             # abroad,    political,    society,     economy, 
pages = [10, 9, 14, 2]

direct_URLs = []
for c, p in zip(categories, pages):
    for i in range(p-2):
        url = 'https://novychas.online/' + c + '?page=' + str(i)
        print(url)
        header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        response = requests.get(url, headers=header)
        soup = BeautifulSoup(response.content, 'html.parser')
        for item in soup.find_all('article', {'class' : 'col-sm-6 col-lg-4 card article-card'}):
            direct_URLs.append(item.find('a')['href'])
        print('now collected', len(direct_URLs), 'articles from previous pages...')

direct_URLs = ['https://novychas.online/' + i for i in direct_URLs]
final_result = list(set(direct_URLs))   

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
#             print("newsplease maintext: ", article['maintext'])
            print("newsplease title: ", article['title'])
#             print("newsplease date: ",  article['date_publish'])
            
            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser')

            # fix main text
            if not article['maintext']:
                try:
                    maintext = soup.find("div", {"class":"novychas-article-body"}).text.strip()
                    article['maintext']  = maintext
                except:
                    try:
                        soup.find("div", {"class":"publication-body col col-lg-9 col-xl-7"}).find_all('p')
                        maintext = ''
                        for i in soup.find("div", {"class":"publication-body col col-lg-9 col-xl-7"}).find_all('p'):
                            maintext += i.text.strip()
                        article['maintext'] = maintext
                    except:
                        article['maintext']  = None
                        
            if article['maintext']:
                print("newsplease maintext: ", article['maintext'][:50])
            
            # fix date
            if not article['date_publish']:
                try:
                    date = soup.find("meta", {'property' : "article:published_time"})['content']
                    article['date_publish'] = dateparser.parse(date).replace(tzinfo=None)
                except:
                    try:
                        date = soup.find("time")['datetime']
                        article['date_publish'] = dateparser.parse(date).replace(tzinfo=None)
                    except:
                        article_date = None
                        article['date_publish'] = None  
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


