
# Packages:
from pymongo import MongoClient
import bs4
from bs4 import BeautifulSoup
from newspaper import Article
from dateparser.search import search_dates
import dateparser
import requests
from urllib.parse import quote_plus

from random import randint, randrange
from warnings import warn
import json
from pymongo import MongoClient
from urllib.parse import urlparse
from datetime import datetime
from pymongo.errors import DuplicateKeyError
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from dotenv import load_dotenv

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p


#####################
# collect more URLs #
#####################
source = 'alakhbar.info'

categories = [ 'news', 'taxonomy/term/986', 'eco', 'taxonomy/term/993', 'international', 'taxonomy/term/954']
                     # communities, accidents and society, international news, opinion
page_start = [1,1,1,1,1, 1]
page_end = [140, 2, 2, 2, 20, 18]

for c, ps, pe in zip(categories, page_start, page_end):
    direct_URLs = []

    for i in range(ps, pe+1):
        link = 'http://alakhbar.info/?q=' + c + '&page=' + str(i)
        print(link)
        try: 
            hdr = {'User-Agent': 'Mozilla/5.0'}
            req = requests.get(link, headers = hdr)
            soup = BeautifulSoup(req.content)

            item = soup.find_all('h1')
            for i in item:
                try:
                    direct_URLs.append(i.find('a', href = True)['href'])
                except:
                    pass
            print('Now scraped ', len(direct_URLs), ' articles from previous page.')
        except:
            pass



    # modify direct URLs

    direct_URLs =list(set(direct_URLs))


    final_result = ['http://alakhbar.info' + i for i in direct_URLs]
    print('Total number of urls found: ', len(final_result))


    ######################
    # scrape direct URLs #
    ######################

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

                #############################
                # change source_domain here #
                #############################
                
                article['source_domain'] = source
                
                #print("newsplease date: ", article['date_publish'])

                soup = BeautifulSoup(response.content, 'html.parser')
        
                if article['date_publish'] :
                    print('Scraped date: ', article['date_publish'] )


                if article['title']:
                    print('Scraped title: ', article['title'] )


                if article['maintext']:
                    print('Scraped maintext: ', article['maintext'][:50])

                try:
                    year = article['date_publish'].year
                    month = article['date_publish'].month

                    print(c)
                    if c == "taxonomy/term/954":
                        article['primary_location'] = 'MRT'
                        colname = f'opinion-articles-{year}-{month}'
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
                    if colname != 'articles-nodate':
                        url_count = url_count + 1
                        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                    else:
                        print("Inserted! in ", colname)
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
