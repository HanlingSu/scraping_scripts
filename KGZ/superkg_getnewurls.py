from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from random import randint, randrange
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import cloudscraper


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'super.kg'

direct_URLs = []    
categories = ['5',  '43',     '65',                     '41',       '9',            '7']
        #POLITICS  society   Legal cases in politics    world   CRIMES & ACCIDENTS, PUBLIC NEWS
page_start = [1, 1, 1, 1, 1, 1]
page_end = [15, 40, 1, 22, 15, 1]
# page_end = [964, 1294, 13, 277, 659, 71 ]


scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)

base = 'https://www.super.kg/kabar/category/'

for c, ps, pe in zip(categories, page_start, page_end):
    for p in range(ps, pe+1):
        link = base + c +'?page=' + str(p) 
        print(link)
        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
#         req = requests.get(link, headers = hdr)
        soup = BeautifulSoup(scraper.get(link).text)
        item = soup.find_all('div', {'class' : 'mt-4 d-flex flex-row jitem'})
        for i in item:
            url = i.find('a')['href']
            direct_URLs.append(url)

        print(len(direct_URLs))

final_result = list(set(direct_URLs))
print(len(final_result))

url_count = 0
processed_url_count = 0

for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            header ={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'} #header settings

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

            # date
            try:
                date = soup.find('time', {'itemprop' : ' datePublished'})['content']
                article['date_publish'] = dateparser.parse(date).replace(tzinfo = None)
            except:
                date = soup.find('time')['datetime']
                article['date_publish'] = dateparser.parse(date).replace(tzinfo = None)
            print("newsplease date: ",  article['date_publish'])

            # main text
            try:
                maintext = soup.find('div', {'class' : 'inside-text'}).text
                article['maintext'] = maintext.strip()
            except:
                maintext = ''
                soup.find('div', {'class' : 'inside-text'}).find_all('p')
                for i in  soup.find('div', {'class' : 'inside-text'}).find_all('p'):
                    maintext += i.text
                article['maintext'] = maintext.strip()

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
