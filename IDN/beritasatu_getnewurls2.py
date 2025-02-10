
# Packages:
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
import re
import json

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

url_count = 0
processed_url_count = 0

source = 'beritasatu.com'
direct_URLs = []

categories= ['nasional', 'megapolitan', 'nusantara', 'ekonomi', 'internasional']
                #main       immediate news  local news          world news
page_start = [1, 1, 1, 1, 1]
page_end = [120, 700, 35, 90, 40]
# only change before each update

for c, ps, pe in zip(categories, page_start, page_end):
    for i in range(ps, pe+1):
        link = 'https://www.beritasatu.com/' + c + '/indeks/' + str(i)
        print(link)
        hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        req = requests.get(link, headers = hdr)
        soup = BeautifulSoup(req.content)
        items = soup.find_all('div', {'class' : 'row gx-3 mt-4 position-relative'})
        for item in items:
            direct_URLs.append(item.find('a')['href'])
            
        print('Now collected ', len(direct_URLs), 'articles from previous pages...')

# direct_URLs = ['https://www.beritasatu.com' + i for i in direct_URLs ]

blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
final_result = [word for word in direct_URLs if not blacklist.search(word)]


print(len(final_result))
for url in final_result:
    if url:
        
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
            
        
            soup = BeautifulSoup(response.content, 'html.parser')
            url = soup.find('meta', property = 'og:url')['content']
            article['url'] = url
            print(url, "FINE")
            print("newsplease title: ", article['title'])

            # fix date
            try:
                date = soup.find_all('script', type="application/ld+json")[1].string.split('"datePublished":', 1)[1].split(',', 1)[0]
                        
                date_publish = dateparser.parse(date).replace(tzinfo = None) 
                article['date_publish'] = date_publish

            except:
                try:
                    date = json.loads(soup.find_all('script', type = 'application/ld+json')[1].contents[0])['datePublished']
                    date_publish = dateparser.parse(date).replace(tzinfo = None) 
                    article['date_publish'] = date_publish
                except:
                    try:
                        date = soup.find('span', {'class' : 'text-muted'}).text
                        date_publish = dateparser.parse(date).replace(tzinfo = None) 
                        article['date_publish'] = date_publish
                    except:
                        article['date_publish'] = None
            print("newsplease date: ", article['date_publish'])
            
            # fix main text
            if article['maintext']:
                article['maintext'] = article['maintext'].replace('Beritasatu.com -', '')
            else:
                try:
                    if len(soup.find_all('div', {'class': 'story'})) > 1:
                        maintext = soup.find_all('div', {'class': 'story'})[1].text
                        article['maintext'] = maintext.strip().replace('Beritasatu.com -', '')
                    

                except:
                    try:
                        maintext = soup.find('div', {'class':"story"}).text
                        article['maintext'] = maintext.strip().replace('Beritasatu.com -', '')

                    except:
                        article['maintext'] = article['maintext'].replace('Beritasatu.com –', '')

            if article['maintext']:
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
direct_URLs = []
print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")

