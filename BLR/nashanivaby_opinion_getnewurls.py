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

direct_URLs = []

# for year in range(2023, 2024):
#     year_str = str(year)
#     for month in range(9, 13):
#         month_str = str(month)
#         print('Now scraping articles published in ', year_str, '-', month_str)
#         for day in range(1, 32):
#             day_str = str(day)
#             for page in range(1,4):
#                 page_str = str(page)
#                 link = 'https://nashaniva.com/?c=shdate&i=' + year_str + '-' + month_str + '-' + day_str + '&p=' + page_str +'&lang=ru'
#                 print(link)
#                 hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
#                 req = requests.get(link, headers = hdr)
#                 soup = BeautifulSoup(req.content)
#                 item =  soup.find_all('div', {'class' : 'posts-grid_p50'})
#                 for i in item:
#                     direct_URLs.append(i.find('a')['href'])
#             print('Now collected ', len(direct_URLs), 'articles from previous months...')

url = 'https://nashaniva.com/?c=ca&i=602&p='
for p in range(1, 5):
    hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
    link = url + str(p)
    print(link)
    req = requests.get(link, headers = hdr)
    soup = BeautifulSoup(req.content)
    item =  soup.find_all('h2', {'class' : 'news-title'})
    for i in item:
        direct_URLs.append(i.find('a')['href'])
    print('Now collected ', len(direct_URLs), 'articles from previous months...')

print(len(direct_URLs))

final_result = list(set(direct_URLs))
final_result = ['https://nashaniva.com' + i for i in final_result if 'https://nashaniva.com' not in i]
print(len(final_result))

url_count = 0
processed_url_count = 0 
source = 'nashaniva.by'
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
      

           
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                # colname = f'articles-{year}-{month}'
                colname = f'opinion-articles-{year}-{month}'

                
            except:
                colname = 'articles-nodate'
            
            # Inserting article into the db:
            try:
                db[colname].insert_one(article)
                # count:
                if colname != 'articles-nodate':
                    url_count = url_count + 1
                    print("Inserted! in ", colname, " - number of urls so far: ", url_count)
            except DuplicateKeyError:
                db[colname].delete_one({'url' : url})
                db[colname].insert_one(article)
                
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