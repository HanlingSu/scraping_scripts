
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
import cloudscraper


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'guardian.ng'
# base = 'https://guardian.ng/?s=&page=2' 
# for p in range(1, 50):
#     hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
#     link = base  + str(p)
#     print(link)
#     req = requests.get(link, headers = hdr)
#     soup = BeautifulSoup(req.content)
#     item = soup.find_all('span', {'class' : 'title'})
#     for j in item:
#         try:
#             direct_URLs.append(j.find('a')['href'])
#         except:
#             pass
#     # print(direct_URLs)
#     print('Now scraped ', len(direct_URLs), ' articles from previous pages.')


scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)

hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


category = [ 'opinion']
page_start = [ 99]
page_end = [ 198]

base = 'https://guardian.ng/category/' 
for c, ps, pe in zip(category, page_start, page_end):
    for p in range(ps, pe):
        direct_URLs = []

        link = base + c + '/page/' +str(p)
        hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

        print(link)
        req = requests.get(link, headers = hdr)
        soup = BeautifulSoup(req.content)
        item = soup.find_all('span', {'class' : 'title'})
        for j in item:
            try:
                link = j.find('a')['href']
                direct_URLs.append(link)
            except:
                pass
        # print(direct_URLs)
        print('Now scraped ', len(direct_URLs), ' articles from previous pages.')


        blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
        blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
        direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

        final_result = list(set(direct_URLs))

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
                    response = requests.get(link, headers=hdr)
                    soup = BeautifulSoup(scraper.get(url).text)
                    article = NewsPlease.from_html(scraper.get(url).text).__dict__


                    article['date_download']=datetime.now()
                    article['download_via'] = "Direct2"
                    article['source_domain'] = source
                    article['url'] = url
                    print("newsplease title: ", article['title'])

                    print("newsplease maintext: ", article['maintext'][:50])

                    print("newsplease date: ", article['date_publish'])


                    try:
                        year = article['date_publish'].year
                        month = article['date_publish'].month
                        if '/opinion/' in url:
                            colname = f'opinion-articles-{year}-{month}'
                            article['primary_location'] = 'NGA'
                        else:
                            colname = f'articles-{year}-{month}'
                        #print(article)
                    except:
                        colname = 'articles-nodate'
                    #print("Collection: ", colname)
                    try:
                        #TEMP: deleting the stuff i included with the wrong domain:
                        myquery = { "url": url, "source_domain" : source}
                        db[colname].delete_one(myquery)
                        # Inserting article into the db:
                        db[colname].insert_one(article)
                        # count:
                        if colname != 'articles-nodate':
                            url_count = url_count + 1
                            print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        else:
                            print("Inserted! in ", colname)
                        db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        myquery = { "url": url, "source_domain" : source}
                        db[colname].delete_one(myquery)
                        # Inserting article into the db:
                        db[colname].insert_one(article)
                        print("DUPLICATE! Not inserted.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
                processed_url_count += 1
                print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")

