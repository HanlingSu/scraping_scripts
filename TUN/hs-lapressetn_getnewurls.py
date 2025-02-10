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


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'lapresse.tn'

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

categories = ['actualites', 'international', 'economie', 'societe', 'editorial']

page_start = [1, 1, 1, 1, 1 ]
page_end = [140,25,85,100, 7]

base = 'https://lapresse.tn/category/'


for c, ps, pe in zip(categories, page_start, page_end):
    for i in range(ps, pe+1):
        direct_URLs = []

        link = base + c + '/page/' + str(i)
        print(link)
        reqs = requests.get(link, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        for h2 in soup.find_all('h2', {'class' : 'entry-title'}):
            try:
                direct_URLs.append(h2.find('a')['href'])

            except:
                pass

        print(len(direct_URLs))


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
                    print("newsplease maintext: ", article['maintext'][:50])                    
                    
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # fixing some titles:
                    if article['title'] == 'La Presse de Tunisie':
                        try:
                            title = soup.find('h1', {'class': "post-title entry-title"}).text.strip()
                            article['title'] = title

                        except:

                            pass

                    
                    try:
                        year = article['date_publish'].year
                        month = article['date_publish'].month
                        print(c)
                        if c == 'editorial':
                            colname = f'opinion-articles-{year}-{month}'
                            article['primary_location'] = "TUN"
                        else:
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
