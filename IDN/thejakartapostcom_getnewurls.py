# Packages:
from unicodedata import category
from pymongo import MongoClient
from bs4 import BeautifulSoup
from dateparser.search import search_dates
import dateparser
import requests
from urllib.parse import quote_plus
import time
from datetime import datetime
from pymongo.errors import DuplicateKeyError
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from dotenv import load_dotenv

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# base = 
categories = ['indonesia/politics', 'indonesia/jakarta', 'indonesia/society', 'indonesia/archipelago', 'business/economy', \
    'world/asia-pacific', 'world/americas', 'world/europe', 'world/middle-east-africa', 'life/health']

base = 'https://www.thejakartapost.com/'

page_start = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
# page_end = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

page_end = [12, 3, 6, 7, 7, 10, 5, 5, 2, 2 ]
for c, ps, pe in zip(categories, page_start, page_end):
    direct_URLs = []

    for p in range(ps, pe+1):

        link = base + c + '?page=' + str(p)
        
        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
        req = requests.get(link, headers = hdr)
        soup = BeautifulSoup(req.content)
        item = soup.find_all('div', {'class' : 'imageLatest'})

        for i in item:
            direct_URLs.append(i.find('a')['href'])


    print('Now scraped ', len(direct_URLs), ' articles from previous pages.')

    final_result = ['https://www.thejakartapost.com' + i for i in direct_URLs]

    len(final_result)

    url_count = 0
    processed_url_count = 0
    source = 'thejakartapost.com'
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
                
    #             print('custom parsed date: ', article['date_publish'])
                print('custom parsed title: ', article['title'])
    #             print('custom parser maintext', article['maintext'])

                # custom parser
                soup = BeautifulSoup(response.content, 'html.parser')
            
                    
                # fix date
                try:
                    date = soup.find('span', {'class':"day"}).text
                    article['date_publish'] = dateparser.parse(date)

                except:
                    article['date_publish'] = article['date_publish']
                    
                if article['date_publish']:
                    print('custom parser date:', article['date_publish'])
                    

                # Get Main Text:
                try:
                    soup.find('div', {'class' : 'col-md-10 col-xs-12 detailNews'}).find_all('p')
                    maintext = ''
                    for i in soup.find('div', {'class' : 'col-md-10 col-xs-12 detailNews'}).find_all('p'):
                        maintext += i.text.strip()
                    article['maintext'] = maintext
                except:
                    article['maintext']  = article['maintext']
                if article['maintext']:
                    print('custom parsed maintext: ', article['maintext'][:50])


        
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
