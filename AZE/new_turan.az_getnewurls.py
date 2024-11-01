
from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from random import randint, randrange
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []

sitemap = 'https://turan.az/storage/sitemap/az/sitemap_index_0.xml'

hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
req = requests.get(sitemap, headers = hdr)
soup = BeautifulSoup(req.content)
item = soup.find_all('loc')
for i in item:
    url = i.text
    direct_URLs.append(url)

print(len(direct_URLs))

final_result = direct_URLs.copy()[1000:3000]
print(len(final_result))

url_count = 0
processed_url_count = 0
source = 'turan.az'
for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            hdr = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            response = requests.get(url, headers=hdr)
            
            article = NewsPlease.from_html(response.text, url=url).__dict__
           
            soup = BeautifulSoup(response.content)

            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            # title has no problem
            
            # process


            # custom parser
            
            try:
                date = soup.find('meta', {'name' : 'og:article:published_time'})['content']
                article['date_publish'] = dateparser.parse(date).replace(tzinfo=None)
            except:
                date = soup.find('ul', {'class' : 'nav meta'}).text.split('\n')[2].strip()
                article['date_publish'] = dateparser.parse(date)

            try:
                maintext = ''
                for i in soup.find('div', {'class' : 'post--content some-class-name2'}).find_all('p'):
                    maintext += i.text
                article['maintext'] = maintext.strip()
            except:
                article['maintext'] = soup.find('div', {'class' : 'post--content some-class-name2'}).text.strip()
                
            print("newsplease date: ",  article['date_publish'])
            print("newsplease title: ", article['title'])
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
