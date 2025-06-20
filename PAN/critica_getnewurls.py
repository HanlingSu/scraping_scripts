
from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from random import randint, randrange
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import re 
import pandas as pd
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
sitemap_base = 'https://www.critica.com.pa/nacional?page='
source = 'critica.com.pa'

url_count = 0
processed_url_count = 0


for p in range(2500, 4000):
    direct_URLs = []

    sitemap = sitemap_base+str(p)
    print(sitemap)
    hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
    soup = BeautifulSoup(scraper.get(sitemap).text)
    item = soup.find_all('div', {'class' : 'article-body'})
    for i in item:
        url = i.find('a')['href']
        direct_URLs.append(url)

    print(len(direct_URLs))

    blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0] +['/opinion/']
    blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
    direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

    direct_URLs = ['https://www.critica.com.pa' + i for i in direct_URLs]
    final_result = direct_URLs.copy()
    print(len(final_result))


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
                article['url'] = url
                # title has no problem
                print("newsplease title: ", article['title'])

                try:
                    date = soup.find('meta',  {'property' : 'article:published_time'})['content']
                    article['date_publish'] = dateparser.parse(date)
                except:
                    date = soup.find('time').text
                    article['date_publish'] = dateparser.parse(date)

                print("newsplease date: ",  article['date_publish'])
                        
                # custom parser
                try:
                    maintext = ''
                    for item in soup.find('div', {'class' : 's12 col notas'}).find_all('p'):
                        maintext+= item.text
                    article['maintext'] = maintext.strip()
                except:
                    article['maintext'] = article['maintext'] 

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
                    # myquery = { "url": url, "source_domain" : source}
                    # db[colname].delete_one(myquery)
                    # db[colname].insert_one(article)
                    print("DUPLICATE! PASS.")
                    pass
                    
            except Exception as err: 
                print("ERRORRRR......", err)
                pass
            processed_url_count += 1
            print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')
        else:
            pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
