# Packages:
from unicodedata import category
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
from datetime import datetime
from newsplease import NewsPlease
from pymongo.errors import DuplicateKeyError
import dateparser
import re


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'ipn.md'

base = 'https://www.ipn.md/ro/'
categories = ['politica-7965', 'societate-7967', 'economie-7966','special-7978', 'alegeri-2023-8012']

page_start = [1, 1, 1, 1, 1,1]
page_end = [40, 120, 30, 5, 3]
# page_end = [340, 1168, 235, 277, 1008, 667, 133]

direct_URLs = []

for c, ps, pe in zip(categories, page_start, page_end):
    for p in range(ps, 5+1):
        link = base + c + '.html?page=' + str(p)
        # print(link)
        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
        req = requests.get(link, verify=False)

        soup = BeautifulSoup(req.content)
        item = soup.find_all('h2')
        for i in item:
            direct_URLs.append(i.find('a')['href'])
        direct_URLs = list(set(direct_URLs))
        print('Now scraped ', len(direct_URLs), ' articles from previous pages.')


final_result = direct_URLs.copy()
# final_result = list(set(direct_URLs))
print('Total articles scraped', len(final_result))

url_count = 0

processed_url_count = 0
for url in final_result:
    if url:
        print(url, "FINE")
        
        ## SCRAPING USING NEWSPLEASE:
        try:
            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            response = requests.get(url, verify=False)

            # process
            article = NewsPlease.from_html(response.text, url=url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source

            soup = BeautifulSoup(response.content, 'html.parser')

            print('cutsom parser title ', article['title'] )
            try:
                maintext = ''
                for i in soup.find('div', {'class' : 'post-content uli'}).find_all('p'):
                    maintetx += i.text
                article['maintext'] = maintext.strip()
            except:
                article['maintext'] = soup.find('div', {'class' : 'post-content uli'}).text.strip()

            if  article['maintext']:
                print('custom parser maintext', article['maintext'][:50])
            
            # custom parser
            

            print('custom parser date:', article['date_publish'])
            

            
            
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
