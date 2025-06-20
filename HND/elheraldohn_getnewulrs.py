# Packages:
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
from datetime import datetime
from newsplease import NewsPlease
from pymongo.errors import DuplicateKeyError
import re

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


direct_URLs = []
source = 'elheraldo.hn'

# scrape search result
base = 'https://www.elheraldo.hn/busquedas/-/search/el/false/false/20250101/20250231/date/true/true/0/0/meta/0/0/0/'

start_page = 1
end_page = 550
# 890
for i in range(start_page, end_page+1):
    base_link = base + str(i) 
    print(base_link)
    req = requests.get(base_link, headers = hdr)
    soup = BeautifulSoup(req.content)
    item = soup.find_all('div', {'class' : 'card-title title'})

    for i in item:
        direct_URLs.append(i.find('a')['href'])
        

    print('Now scraped ', len(direct_URLs), ' articles from previous pages.')

# modify direct URLs
direct_URLs = ['https://elheraldo.hn' + i for i in direct_URLs if 'https://elheraldo.hn' not in i]

blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

final_result = direct_URLs.copy()
print('Total number of urls found for ', source, ': ', len(final_result))


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
            print("newsplease date: ", article['date_publish'])
            print("newsplease title: ", article['title'])
            
            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # fix main text:
            try:
                soup.find('div', {'class' : 'articulo__cuerpo'}).find_all('p', {'class' : None})
                maintext = ''
                for i in soup.find('div', {'class' : 'articulo__cuerpo'}).find_all('p', {'class' : None}):
                    maintext += i.text.strip()
                article['maintext'] = maintext
            except:
                article['maintext'] = article['maintext']
                
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
