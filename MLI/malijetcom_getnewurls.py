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

source = 'malijet.com'

base = 'https://malijet.com/'
categories = ['actualte_dans_les_regions_du_mali', 'actualite-politique-au-mali', 'actualite_internationale',\
    'actualite_economique_du_mali', 'a_la_une_du_mali', 'la_societe_malienne_aujourdhui', 'communiques-de-presse']

page_start = [6, 13, 26, 11, 14, 14, 2]
page_end = [6, 13, 26, 11, 14, 14, 2]

direct_URLs = []

for c, ps, pe in zip(categories, page_start, page_end):
    for p in range(ps+1, pe+2):
        link = base + c + '/?page=' + str(p) 
        print(link)
        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
        req = requests.get(link, headers = hdr)
        soup = BeautifulSoup(req.content)
        item = soup.find_all('h5', {'class' : 'card-title text-left'})
        for i in item:
            direct_URLs.append(i.find('a')['href'])
        print('Now scraped ', len(direct_URLs), ' articles from previous pages.')

blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

final_result = direct_URLs.copy()
final_result = list(set(final_result))

print('Total articles scraped', len(final_result))

url_count = 0
source = 'malijet.com'
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
            article['language'] = 'fr'
#             print('custom parser date:', article['date_publish'])
            print('cutsom parser title ', article['title'] )
#             print('custom parser maintext', article['maintext'][:50])
            
            
            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # fix date
            try:
                date = soup.find('p', {'id' : 'date_content'}).text
                date = date.replace('Date : ', '')
                date = date.replace('ao�t', 'august')
                article['date_publish'] = dateparser.parse(date) 
            except:
                date = None 
                article['date_publish'] = None
            print('custom parser date:', article['date_publish'])
            
            # fix Main Text:
            try:
                soup.find('div', {'id': 'article_body'})
                maintext = ''
                for i in soup.find('div', {'id': 'article_body'}).find_all('p'):
                    maintext += i.text
                article['maintext'] = maintext.strip()
            except: 
                try:
                    maintext = soup.find('div', {'id' : 'article_body2'}).text
                    article['maintext'] = maintext
                except: 
                    article['maintext']  = article['maintext']
            print('custom parser maintext', article['maintext'][:50])
            
            
            
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
