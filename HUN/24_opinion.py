
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
import langid


scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)

hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p


sitemap_base = 'https://24.hu/velemeny/page/'
source = '24.hu'


# 36
for i in range(1, 3):
    direct_URLs = []
    
    sitemap = sitemap_base + str(i) 
    print(sitemap  )
    hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
    req = requests.get(sitemap, headers = hdr)
    soup = BeautifulSoup(req.content)
    item = soup.find_all('h3', {'class' : 'm-articleWidget__title -fsMedium'})
    for i in item:
        try:
            url = i.find('a')['href']
            direct_URLs.append(url)
        except:
            pass
    print(len(direct_URLs))
    final_result = direct_URLs.copy()
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

                soup = BeautifulSoup(scraper.get(url).text)
                article = NewsPlease.from_html(scraper.get(url).text).__dict__
                # add on some extras
                article['date_download']=datetime.now()
                article['download_via'] = "Direct2"
                article['source_domain'] = source
 
         


                if article['title'] is not None:
                    print('Title modified!', article['title'])

                if article['maintext'] is not None:
                    print('Maintext modified!',  article['maintext'][:50])       

                if article['date_publish']:
                    print('Manually collected date is ', article['date_publish'])

    


                try:
                    year = article['date_publish'].year
                    month = article['date_publish'].month
                    colname = f'opinion-articles-{year}-{month}'
                    article['primary_location'] = "HUN"

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
                    myquery = { "url": url, "source_domain" : source}
                    # db[colname].delete_one(myquery)
                    # db[colname].insert_one(article)
                    print("DUPLICATE! pass.")
                    pass

            except Exception as err: 
                print("ERRORRRR......", err)
                pass
            processed_url_count += 1
            print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')
        else:
            pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")

