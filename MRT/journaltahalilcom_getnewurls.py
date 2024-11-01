# Packages:
from pymongo import MongoClient
import bs4
from bs4 import BeautifulSoup
from newspaper import Article
from dateparser.search import search_dates
import dateparser
import requests
from urllib.parse import quote_plus

from random import randint, randrange
from warnings import warn
import json
from pymongo import MongoClient
from urllib.parse import urlparse
from datetime import datetime
from pymongo.errors import DuplicateKeyError
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from dotenv import load_dotenv

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []
for category in ['politique', 'economie', 'international', 'actualites']:

    for i in range(1, 6):
        link = 'https://www.journaltahalil.com/category/'+category+'/page/' + str(i)
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = requests.get(link, headers = hdr)
        soup = BeautifulSoup(req.content)
        for h3 in soup.find_all('h3', {'class' : 'elementor-post__title'}):
            direct_URLs.append(h3.find('a')['href'])
        print(len(direct_URLs))


# categories = ['&id=19', '&id=3&subid=4', '&id=3&subid=5', '&id=3&subid=6', '&id=3&subid=15']
#             # terrorism,    policy,          economy,       society,        international

# page_start = [1, 1, 1, 1, 1]
# page_end = [3, 10, 4, 7, 5]


# for c, ps, pe in zip(categories, page_start, page_end):
#     for i in range(ps, pe+1):
#         link = 'http://www.journaltahalil.com/archives/article.php?page=' + str(i) + c
    
#         try: 
#             hdr = {'User-Agent': 'Mozilla/5.0'}
#             req = requests.get(link, headers = hdr)
#             soup = BeautifulSoup(req.content)
            
#             item = soup.find_all('b')
#             for i in item:
#                 direct_URLs.append(i.find('a', href = True)['href'])
#             print('Now scraped', len(direct_URLs), 'from previous pages ...')
#         except:
#             pass

# # print(direct_URLs[:5])
direct_URLs =list(set(direct_URLs))

# final_result = ['http://www.journaltahalil.com/archives/' + i for i in direct_URLs]
final_result = direct_URLs.copy()
print(len(final_result))
print(final_result[:5])

url_count = 0
processed_url_count = 0
source = 'journaltahalil.com'
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
            article['language'] = 'fr'
            #print("newsplease date: ", article['date_publish'])

            ## Fixing Date:
            soup = BeautifulSoup(response.content, 'html.parser')

          
            try:
                article_date = soup.find('span', {'class' : 'text'}).text
                article_date = dateparser.parse(article_date, settings = {'DATE_ORDER' : 'DMY'})
                article['date_publish'] = article_date
            except:
                article_date = soup.find('span', {'class' :'elementor-icon-list-text elementor-post-info__item elementor-post-info__item--type-date'}).text
                article['date_publish'] = article_date = dateparser.parse(article_date)
            if article['date_publish']:
                print('Date modified! ', article['date_publish'])
                
                
            ## Fixing Title:
            try:
                article_title = soup.find("strong", {"class":"Titre"}).text
                article['title']  = article_title   
            except:
                article_title  = soup.find('h1').text
                article['title'] = article_title
            if article['title']:
                print('Title modified! ', article['title'])
                
                
            # Get Main Text:
            try: 
                soup.find_all('p')
                maintext = ''
                for i in soup.find_all('p'):
                    maintext += i.text
                article['maintext'] = maintext
            except:
                try:
                    maintext = soup.find("td", {"class":"text"}).text
                    article['maintext'] = maintext
                except:
                    maintext = soup.find('div', {'class' : 'elementor-widget-container'}).find_all('p')
                    fmaintext = ''
                    for i in soup.find('div', {'class' : 'elementor-widget-container'}).find_all('p'):
                        maintext += i.text
                    article['maintext'] = maintext
            if article['maintext']:
                print('Maintext modified!', article['maintext'][:50])
                    

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
