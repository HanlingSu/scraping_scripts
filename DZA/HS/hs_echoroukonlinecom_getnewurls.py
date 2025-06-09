
from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from random import randint, randrange
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import langid
import cloudscraper


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)
sitemap_base = 'https://www.echoroukonline.com/post-sitemap'

# 36
for i in range(455, 465):
    sitemap = sitemap_base + str(i) + '.xml'
    print(sitemap  )
    hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
    soup = BeautifulSoup(scraper.get(sitemap).text)
    item = soup.find_all('loc')
    for i in item:
        url = i.text
        direct_URLs.append(url)

    print(len(direct_URLs))

final_result = direct_URLs.copy()[::-1]
print(len(final_result))

url_count = 0
processed_url_count = 0
source = 'echoroukonline.com'

for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            header ={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'} #header settings
            soup = BeautifulSoup(scraper.get(url).text)

            # process
            article = NewsPlease.from_html(scraper.get(url).text).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            article['url'] = url

            # title has no problem
            print("newsplease title: ", article['title'])
            print("newsplease date: ",  article['date_publish'])
                      
            # custom parser
            try:
                maintext = ''
                for i in soup.find('div', {'class' : 'ech-artx'}).find_all('p'):
                    maintext += i.text
                article['maintext'] = maintext.strip()
            except:
                maintext = soup.find('div', {'class' : 'ech-artx'}).text
                article['maintext'] = maintext.strip()
            print("newsplease maintext: ", article['maintext'][:50])
            
            language, _ = langid.classify(article['maintext'])
            article['language'] = language
            print(article['language'] )

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
                # myquery = { "url": url, "source_domain" : source}
                # db[colname].delete_one(myquery)
                # db[colname].insert_one(article)
                print("DUPLICATE! Pass.")
                pass
                
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')
    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
