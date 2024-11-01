# Packages:

import re
from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from pymongo import MongoClient
from urllib.parse import urlparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from pymongo.errors import CursorNotFound
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []
url_base = 'http://news.acotonou.com/h/'
source = 'news.acotonou.com'

for n in range(154334, 154966):
    url = url_base + str(n) + '.html'
    direct_URLs.append(url)


final_result = direct_URLs.copy()
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
#             print("newsplease maintext: ", article['maintext'][:50])
#             print("newsplease date: ",  article['date_publish'])
            
            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # fix main text
            try:
                maintext = soup.find('span', {'class' : 'FullArticleTexte'}).text.strip()
                article['maintext'] = maintext
            except:
                try:
                    article['maintext'] = str(soup.find_all('script',  {'data-vue-meta':"true", 'type' : 'application/ld+json'})[1]).split('"articleBody":')[1].split('"articleSection":')[0]
                except:
                    article['maintext'] = article['maintext'] 
                
            if article['maintext']:
                print('newsplease maintext', article['maintext'][:50])
            
            # fix date
            try:
                date = soup.find('div', {'class' : 'FontArticleSource'}).text.split('|')[0].split('le', 1)[1]
                article['date_publish'] = dateparser.parse(date)
            except:
                date = ' '.join(soup.find('div', {'class' : 'FontArticleSource'}).text.split(' ')[3:6])
                article['date_publish'] = dateparser.parse(date)
            if article['date_publish']:
                print(article['date_publish'])
                
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
