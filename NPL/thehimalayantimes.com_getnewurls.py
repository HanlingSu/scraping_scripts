# Packages:
from pymongo import MongoClient
from bs4 import BeautifulSoup
from newspaper import Article
import dateparser
import requests
from warnings import warn
from pymongo import MongoClient
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import re
# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

base = 'https://thehimalayantimes.com/sitemaps/'
source = 'thehimalayantimes.com'

for year in range(2024, 2025):
    for month in range(7, 11):
        direct_URLs = []

        sitemap = base + str(year) + '/' + str(month) +'/' + 'sitemap_0.xml?v=1.1'
        print(sitemap)

        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
        req = requests.get(sitemap, headers = hdr)
        soup = BeautifulSoup(req.content)
        item = soup.find_all('loc')
        for i in item:
            url = i.text
            direct_URLs.append(url)
        direct_URLs = list(set(direct_URLs))
        print(len(direct_URLs))

        blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
        blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
        direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]
        final_result = direct_URLs.copy()


        url_count = 0
        processed_url_count = 0


        for url in final_result:
            if url:
                print(url, "FINE")
                ## SCRAPING USING NEWSPLEASE:
                try:
                    #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
                    header = hdr = {'User-Agent': 'Mozilla/5.0'}
                    response = requests.get(url, headers=header)
                    # process
                    article = NewsPlease.from_html(response.text, url=url).__dict__
                    # add on some extras
                    article['date_download']=datetime.now()
                    article['download_via'] = "Direct2"
                    article['source_domain'] = source
                    # title has no problem
                    
                    # custom parser
                    soup = BeautifulSoup(response.content, 'html.parser')
                

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
