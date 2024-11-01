# Packages:
import re
from pymongo import MongoClient

from bs4 import BeautifulSoup
import dateparser
import requests
import json
from pymongo import MongoClient
from urllib.parse import urlparse
from datetime import datetime
from pymongo.errors import DuplicateKeyError
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
import json
import detectlanguage

detectlanguage.configuration.api_key = "81762acd6a7244ef736911adbadb09e3"

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'babnet.net'
base = 'https://www.babnet.net/'

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

categories = ['politique', 'economie', 'regions', 'social', 'sante', 'monde', 'justice', 'tribune']
page_start = [1, 1, 1, 1, 1, 1, 1, 1]
# # page_end = [600, 400, 500, 100, 100, 200, 300]
page_end = [1100, 700, 1200, 300, 180, 510, 390, 30]



direct_URLs = []

for c,ps, pe in zip(categories, page_start, page_end):
    for i in range(ps, pe+1, 30):
        link = base + c + '.php?p=' + str(i)
        print(link)
        reqs = requests.get(link, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        for h2 in soup.find_all('h2', {'class' : 'post-title title-large arabi'}):
            try:
                direct_URLs.append(h2.find('a')['href'])

            except:
                pass

        print('Now collect',len(direct_URLs), 'articles from previous pages ... ')

        direct_URLs = ['https://www.babnet.net/' + i for i in direct_URLs if 'https://www.babnet.net/' not in i]

        final_result = list(set(direct_URLs))

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
                    print("newsplease date: ", article['date_publish'])
                    print("newsplease title: ", article['title'])
                                    
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    try:
                        json_script = str(soup.find_all('script', {'type' : 'application/ld+json'})[1].contents[0])
                        maintext_index = json_script.find('"articleBody"')
                        maintext = json_script[maintext_index+16:-9]
                        article['maintext'] = maintext.strip()
                    except:
                        article['maintext'] = soup.find('div', {'class' : 'box'}).text.strip()

                    print("newsplease maintext: ", article['maintext'][:50])   

                    # code = detectlanguage.detect(article['maintext'])[0]['language']
                    article['language'] = 'ar' 
                    print(article['language'] )

                    try:
                        year = article['date_publish'].year
                        month = article['date_publish'].month
                        if c =="tribune":
                            colname = f'opinion-articles-{year}-{month}'
                            article['primary_location'] = 'TUN'
                        else:
                            colname = f'articles-{year}-{month}'
                        #print(article)
                    except:
                        colname = 'articles-nodate'
                    #print("Collection: ", colname)
                    try:
                        # Inserting article into the db:
                        db[colname].insert_one(article)
                        # count:
                        url_count = url_count + 1
                        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        db[colname].delete_one({'url' : url})
                        db[colname].insert_one(article)
                        print("DUPLICATE! Updated.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
                processed_url_count += 1
                print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

            else:
                pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
