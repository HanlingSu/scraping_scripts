# Packages:
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
from datetime import datetime
import dateparser
from newsplease import NewsPlease
from pymongo.errors import DuplicateKeyError
import re
import cloudscraper


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

sitemap = 'https://www.soy502.com/sitemaps/sitemap.php?page=0'

direct_URLs = []

hdr = {'User-Agent': 'Mozilla/5.0'}
soup = BeautifulSoup(scraper.get(sitemap).text)

item = soup.find_all('loc')
for i in item:
    direct_URLs.append(i.text)
print(len(direct_URLs))

final_result = direct_URLs[5000:5200][::-1]
print(len(final_result))

source = 'soy502.com'
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
#             print("newsplease date: ", article['date_publish'])
            # soup = BeautifulSoup(scraper.get(sitemap).text)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            try:
                category = soup.find('ul', {'class':"section-title"}).text.split('/')[1].strip()
            except:
                category = 'news'

            if category is not None and category in [ 'Fama', 'Deportes', 'Foto-galeria', 'Vida y estilo', 'Videos']:
                article['title']  = 'From uninterested categories!!!'
                article['maintext']  = None
                article['date_publish'] = None
                print('\n', article['title'], category)
                
            else:
                print("newsplease title: ", article['title'])
                try:
                    date = dateparser.parse(soup.find('span', {'class':"date"}).text)
                    article['date_publish'] = date
                    
                except:
                    article['date_publish'] = article['date_publish']
                print("newsplease date: ", article['date_publish'])

                try:
                    soup.find('div', {'class' : 'body tvads'}).find_all('p')
                    maintext = ''
                    for i in soup.find('div', {'class' : 'body tvads'}).find_all('p'):
                        maintext+= i.text
                    article['maintext'] = maintext.strip()
                except:
                    article['maintext'] =soup.find('div', {'class' : 'body tvads'}).text
                if article['maintext']:
                    print("newsplease maintext: ", article['maintext'][:50])                    
                

            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'articles-{year}-{month}'
                #print(article)
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
                # db[colname].delete_one({'url': article['url']})
                # db[colname].insert_one(article)
                print("DUPLICATE! Pass.")
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
