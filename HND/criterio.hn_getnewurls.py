from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
from datetime import datetime
from pymongo.errors import DuplicateKeyError
import requests
from newsplease import NewsPlease
from dotenv import load_dotenv
import dateparser
import re

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []

sitemap_base = 'https://criterio.hn/post-sitemap'

hdr = {'User-Agent': 'Mozilla/5.0'} #header settings

source = 'criterio.hn'

for p in range(3, 4):
    sitemap = sitemap_base + str(p) + '.xml'
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = requests.get(sitemap, headers = hdr)
    soup = BeautifulSoup(req.content)
    for i in soup.find_all('loc'):
        direct_URLs.append(i.text)
    print('Now scraped ', len(direct_URLs), ' articles from previous page.')


final_result = direct_URLs.copy()
print('Total number of urls found: ', len(final_result))


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
            
            ## Fixing Date:
            soup = BeautifulSoup(response.content, 'html.parser')
           
            print("newsplease date: ", article['date_publish'])
            print("newsplease title: ", article['title'])
            article['maintext'] = '\n'.join(article['maintext'].split('\n')[2:])
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
                if colname != 'articles-nodate':
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