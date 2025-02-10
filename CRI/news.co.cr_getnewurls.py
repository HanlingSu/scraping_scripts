
from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from random import randint, randrange
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import json
import cloudscraper

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []

sitemap_base = 'https://news.co.cr/post-sitemap'
source = 'news.co.cr'


hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


for p in range(19, 22):
   
        
        sitemap = sitemap_base + str(p) + '.xml'
        
        print(sitemap)
        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
        response = requests.get(sitemap, verify=False)
        soup = BeautifulSoup(response.content)
        item = soup.find_all('loc')
        for i in item:
            url = i.text
            direct_URLs.append(url)
        print(len(direct_URLs))


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

            # custom parser
            response = requests.get(url, verify=False)

            soup = BeautifulSoup(response.content)
            # 
            article = NewsPlease.from_html(response.text, url=url).__dict__

            
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            article['url'] = url  
            # title has no problem
            categories = soup.find('ul', {'class' : 'post-categories'}).text.split('\n')

            blacklist = ['Technology News', 'Sports News', 'Entertainment', 'Science News', 'Technology News']

            if any(category.strip() in blacklist for category in categories):
                article['title'] = "From uninterested category"
                article['maintext'] = None
                article['date_publish'] = None
                print(article['title'])
            else:
                    
                print("newsplease title: ", article['title'])
                print("newsplease maintext: ", article['maintext'][:50])
                print("newsplease date_publish: ",   article['date_publish'])

                
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
                    # db['urls'].insert_one({'url': article['url']})
                except DuplicateKeyError:
                    myquery = { "url": url, "source_domain" : source}
                    # db[colname].delete_one(myquery)
                    # db[colname].insert_one(article)
                    print("DUPLICATE! Update.")
                    pass
                
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')
    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
