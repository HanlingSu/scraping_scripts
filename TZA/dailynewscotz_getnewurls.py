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


source = 'dailynews.co.tz'

# find primary location:
documents = db.sources.find({'source_domain': source}, { 'source_domain':1, 'primary_location': 1, '_id': 0 })
for document in documents:
    primary_location = document['primary_location']

# categories for scraping
categories = ['tanzania','world','politics', 'society-culture', 'business', 'health', 'opinions']
page_start = [1, 1, 1, 1, 1, 1, 1]
# page_end = [1, 1, 1, 1, 1, 1]
page_end = [100, 25, 21, 30, 45, 12, 9  ]


url_count = 0
processed_url_count = 0

for c, ps, pe in zip(categories, page_start, page_end):
    direct_URLs = []

    for i in range(ps, pe+1):
        link = 'https://dailynews.co.tz/category/' + c +'/page/' + str(i)
        print(link)
     # mundo, nacionales, noticias-del-dia, espectaculos, ciencia
        
        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
        req = requests.get(link, headers = hdr)
        soup = BeautifulSoup(req.content)
        item = soup.find_all('h2')
        for i in item:
            direct_URLs.append(i.find('a')['href'])

        print(len(direct_URLs))

    final_result = list(set(direct_URLs))
    print(len(final_result))


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
                print("newsplease maintext: ", article['maintext'][:50])
                
                # custom parser
                soup = BeautifulSoup(response.content, 'html.parser')
                
                try:
                    #article_title = soup.find("title").text
                    contains_article = soup.find("meta", {"property":"og:title"})
                    article_title = contains_article['content'].replace(' - Daily News', '')
                    article['title']  = article_title   
                except:
                    try:
                        article['title']  = soup.find('h1', {'class' : 'post-title entry-title'}).text
                    except:
                        article_title = None
                        article['title']  = None
                print("newsplease title: ", article['title'])
                
                try:
                    contains_date = soup.find("meta", property = "article:published_time")['content']
                    article_date = dateparser.parse(contains_date)
                    article['date_publish'] = article_date
                except:
                    try:
                        contains_date = soup.find("span", {"class":"date meta-item tie-icon"}).text
                        article_date = dateparser.parse(contains_date)
                        article['date_publish'] = article_date
                    except:
                        article_date = None
                        article['date_publish'] = article['date_publish']  
                print("newsplease date: ",  article['date_publish'])
                
                try:
                    year = article['date_publish'].year
                    month = article['date_publish'].month
                    if c == 'opinions':
                        colname = f'opinion-articles-{year}-{month}'
                        article['primary_location'] = primary_location

                    else:
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
