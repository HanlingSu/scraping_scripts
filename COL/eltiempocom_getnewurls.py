
# Packages:
from typing import final
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import dateparser
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import re

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
direct_URLs = []
source = 'eltiempo.com'

# sitemap_base = 'https://www.eltiempo.com/sitemap-articles-'
for year in range(2025, 2026):
    year_str = str(year)
    for month in range(1, 5):
        if month<10:
            month_str = '0' + str(month)
        else:
            month_str = str(month)
            
        for day in range(1, 32):

            if day<10:
                day_str = '0' + str(day)
            else:
                day_str = str(day)


            date_str = year_str+'-'+month_str+'-'+day_str

            for p in range(1, 30):
                
                link =  'https://www.eltiempo.com/buscar/?q=el&sort_field=desc&articleTypes=default&categories_ids_or=&from='+date_str+'&until='+date_str+'&page='+str(p)
                hdr = {'User-Agent': 'Mozilla/5.0'}
                req = requests.get(link, headers = hdr)
                soup = BeautifulSoup(req.content)
                items = soup.find_all('h3', {'class' : 'c-article__title'})
                for i in items:
                    direct_URLs.append(i.find('a')['href'])
                direct_URLs = list(set(direct_URLs))
            print('Now scraping', date_str)
            print('Now collected ', len(direct_URLs), 'articles from previous date...')


direct_URLs = ['https://www.eltiempo.com' + i for i  in direct_URLs if 'https://www.eltiempo.com' not in i]

blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

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
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            response = requests.get(url, headers=header)
            # process
            article = NewsPlease.from_html(response.text, url=url).__dict__
            soup = BeautifulSoup(response.content, 'html.parser')

          
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            print("newsplease date: ", article['date_publish'])
            print("newsplease title: ", article['title'])

            try:
                maintext = soup.find('div', {'class' : 'c-cuerpo'}).text
                article['maintext'] = maintext.strip()
            except:
                maintext = ''
                for i in soup.find('div', {'class' : 'c-cuerpo'}).find_all('div', {'class': 'paragraph'}):
                    maintext += i.text
                article['maintext'] = maintext.strip()

            print("newsplease maintext: ", article['maintext'][:50])
 

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
                url_count = url_count + 1
                print("Inserted! in ", colname, " - number of urls so far: ", url_count)
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
