# Packages:
from pymongo import MongoClient
from bs4 import BeautifulSoup
from newspaper import Article
from dateparser.search import search_dates
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
from dotenv import load_dotenv

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'lematin.ma'

direct_URLs = []

# base = 'https://lematin.ma/sujet/el/'
# base = 'https://lematin.ma/search?query=la'

# for i in range(1, 100):
#     base_link = base + '&pgno=' + str(i) 
#     print(base_link)
#     hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
#     req = requests.get(base_link, headers = hdr)
#     soup = BeautifulSoup(req.content)
#     item = soup.find_all('a', {'class' : 'article-title'})

#     for i in item:
#         direct_URLs.append(i['href'])


#     print('Now scraped ', len(direct_URLs), ' articles from previous pages.')


direct_URLs = []
categories = ['societe', 'nation', 'monde', 'economie', 'regions', 'activites-royales']
page_start = [1, 1, 1, 1, 1, 1]
page_end = [10, 24, 9, 25, 3]
base = 'https://lematin.ma/'

for c, ps, pe in zip(categories, page_start, page_end):
    for p in range(ps, pe+1):
        base_link = base + c + '?page=' + str(p) 
        print(base_link)
        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
        req = requests.get(base_link, headers = hdr)
        soup = BeautifulSoup(req.content)
        item = soup.find_all('h2')

        for i in item:
            direct_URLs.append(i.find('a')['href'])

        print('Now scraped ', len(direct_URLs), ' articles from previous pages.')
    


final_result = list(set(direct_URLs))
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
            # title, maintext have no problem, need fix date



            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # get category
            try:
                category = soup.find('h3', {'class' : 'title-section mb-2'}).text.strip()
            except:
                category = 'News'

            if category not in ['Sports', 'Lifestyle', 'Automobile', 'Culture', 'Hi-Tech', 'Emploi']:
                
                # fix date
                try:
                    date = soup.find('meta', {'itemprop':'datePublished'})['content']
                    article['date_publish'] = dateparser.parse(date)
                except:
                    try:
                        date = soup.find('time').text
                        article['date_publish'] = dateparser.parse(date)
                    except:
                        article['date_publish'] = article['date_publish']

                if  article['date_publish']:
                    print("newsplease date: ",  article['date_publish'])
            else:
                article['title'] = 'From uninterested categories: ' + category
                article['date_publish'] = None
                article['maintext'] = None
                print(article['title'] )
            
            if article['title']:
                print("newsplease title: ", article['title'])
            if article['maintext']:
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
                else:
                    print("Inserted! in ", colname)
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
