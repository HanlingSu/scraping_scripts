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
import cloudscraper


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p


scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)

direct_URLs = []

categories = ['rajoni', 'antena', 'politika', 'sociale', 'ekonomia', 'bota', 'kronika', ]
page_start = [1,1,1,1]
page_end = []

# base = 'https://www.gazetatema.net/category/kryesore/page/' #1-130
# base = 'https://www.gazetatema.net/category/rajoni/page/' #1-90
base = 'https://www.gazetatema.net/category/aktualitet/page/' #1-950
# base = 'https://www.gazetatema.net/category/antena/page/' #1-20


for i in range(1, 950):
#     link = base + str(i) + '?s=+'
    link = base + str(i)
    print(link)
    hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
    req = requests.get(link, headers = hdr)
    soup = BeautifulSoup(req.content)
    item = soup.find_all('div', {'class' : 'entry-content test_post_grid'})

    for i in item:
        direct_URLs.append(i.find('a')['href'])


    print('Now scraped ', len(direct_URLs), ' articles from previous pages.')

final_result = direct_URLs.copy()
final_result = list(set(final_result))

print('Total number of urls found: ', len(final_result))

url_count = 0
source = 'gazetatema.net'
progress_count = 0
for url in final_result:
    if url:
        print(url, "FINE")
        progress_count += 1
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
            print('custom parser date:', article['date_publish'])
            print('cutsom parser title:', article['title'] )
            
            
            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser')

            # fix Main Text:
            try:
                soup.find('div', {'class': 'entry-content'})
                maintext = ''
                for i in soup.find('div', {'class': 'entry-content'}).find_all('p'):
                    maintext += i.text
                article['maintext'] = maintext
            except: 
                try:
                    soup.find_all('font', {'style' : 'vertical-align: inherit;'})
                    maintext = ''
                    for i in soup.find_all('font', {'style' : 'vertical-align: inherit;'}):
                        maintext += i.text
                    article['maintext'] = maintext
                except:
                    maintext = None
                    article['maintext']  = maintext

            print('custom parser maintext:', article['maintext'][:50])
            
            
            
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
        
        print('.............Now scraped ', progress_count, 'articles...........')
    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
