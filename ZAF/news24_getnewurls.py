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
import pandas as pd
import cloudscraper

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)
# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# sitemap = 'https://www.news24.com/news24/sitemap.sitemap?id=1'
# reqs = requests.get(sitemap, headers=headers)
# soup = BeautifulSoup(reqs.text, 'html.parser')


# for i in soup.find_all('loc'):
#     direct_URLs.append(i.text)
# print(len(direct_URLs))

final_result = list(pd.read_csv('Downloads/peace-machine/peacemachine/getnewurls/ZAF/news24.csv')['0'])
print(len(final_result))

source = 'news24.com'
url_count = 0
processed_url_count = 0
for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            # process
            article = NewsPlease.from_html(scraper.get(url).text).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            article['url'] = url
            print("newsplease title: ", article['title'])
#             print("newsplease maintext: ", article['maintext'][:50])

           
            soup = BeautifulSoup(scraper.get(url).text)

            try:
                maintext = soup.find('div', {'class' : 'article__body NewsArticle'}).text
                article['maintext'] = maintext.strip()
            except: 
                try:
                    maintext = soup.find('div', {'class' : 'caption'}).text
                    article['maintext']  = maintext.strip()
                except:
                    try:
                        maintext = soup.find('div', {'class' : 'article__body--locked'}).text
                        article['maintext']  = maintext.strip()
                    except:
                        article['maintext']  =  article['maintext']
            print("newsplease maintext: ", article['maintext'][:50])
            
            
            
            try:
                date = soup.find('meta', property = 'article:published_time')['content']
                article['date_publish'] = dateparser.parse(date).replace(tzinfo=None)

            except:
                try:
                    date = soup.find('p', {'class' : 'article__date'}).text
                    article['date_publish'] = dateparser.parse(date).replace(tzinfo=None)

                except:
                    try:
                        date = soup.find('meta', {'name' : 'publisheddate'})['content']
                        article['date_publish'] = dateparser.parse(date)
                    except:
                        try:
                            date = soup.find('meta', {'name' : 'article-pub-date'})['content']
                            article['date_publish'] = dateparser.parse(date)
                        except:
                            try:
                                date = soup.find('span', {'class' : 'block datestamp'}).text
                                article['date_publish'] = dateparser.parse(date)
                            except:
                                date = None 
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
                db[colname].insert_one(article)
                # count:
                if colname != 'articles-nodate':
                    url_count = url_count + 1
                    print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                else:
                    print("Inserted! in ", colname)
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

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
