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

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []
source = 'panamaamerica.com.pa'


# link = "https://www.panamaamerica.com.pa/servicios/sitemap/archivo/noticias_2024.xml"

# print(link)
# hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
# req = requests.get(link, headers = hdr)
# soup = BeautifulSoup(req.content)
# for i in soup.find_all('loc'):
#     direct_URLs.append(i.text)
# print(len(direct_URLs))

base = 'https://www.panamaamerica.com.pa/'
category = ['politica', 'sociedad', 'judicial', 'provincias', 'mundo', 'aldea-global', 'sucesos', 'economia']
page_start = [1, 1, 1, 1, 1, 1, 1, 1]
page_end = [20, 20, 20, 30, 10, 10, 10, 10]

for c, ps, pe in zip(category, page_start, page_end):
    for p in range(5, 10):
        link = base + c + '?page=' + str(p)
        print(link)
        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
        req = requests.get(link, headers = hdr)
        soup = BeautifulSoup(req.content)
        for i in soup.find_all('div', {'class' : 'title-wrapper titulo'}):
            direct_URLs.append(i.find('a')['href'])
        print(len(direct_URLs))

direct_URLs = ['https://www.panamaamerica.com.pa' + i for i in direct_URLs]


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
            header ={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'} #header settings

            response = requests.get(url, headers=header)
            # process
            article = NewsPlease.from_html(response.text, url=url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source

            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser')

       

            print("newsplease title: ", article['title'])
            print("newsplease date: ",  article['date_publish'])
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
                myquery = { "url": url, "source_domain" : source}
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
