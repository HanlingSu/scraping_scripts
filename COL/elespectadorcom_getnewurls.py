# Packages:
from typing import final
from unicodedata import category
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import dateparser
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import re
import json

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
direct_URLs = []
source = 'elespectador.com'



categories= ['colombia', 'mundo', 'judicial', 'politica', 'investigacion', 'bogota', 'economia', 'salud']
# pages = [100, 100, 1000, 100, 100, 100, 100, 100 ]
page_start = [0,0,0,0,0,0,0,0]
page_end = [700, 1300, 900, 1200, 50, 1300, 1200, 200 ]
# page_end = [700, 1600, 900, 400, 100, 1500, 1100]
for c, ps, pe in zip(categories, page_start, page_end):
    for i in range(ps, pe+1, 100):
        link = 'https://www.elespectador.com/arc/outboundfeeds/sitemap/section/' + c + '?outputType=xml&size=100&from=' + str(i)
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = requests.get(link, headers = hdr)
        soup = BeautifulSoup(req.content)
        items = soup.find_all('loc')
        for item in items:
            direct_URLs.append(item.text)
            
        print('Now collected ', len(direct_URLs), 'articles from previous pages...')
    

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
            response = requests.get(url, headers=header)
            # process
            article = NewsPlease.from_html(response.text, url=url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            print("newsplease date: ", article['date_publish'])
            
            ## Fixing Date:
            soup = BeautifulSoup(response.content, 'html.parser')

            try:
                article_title = soup.find("meta", property = 'og:title')['content']
                article['title']  = article_title 
            except:
                article_title = None
                article['title']  = None
            print("newsplease title: ", article['title'])

            if not article['date_publish']:
                try:
                    date = dateparser.parse(soup.find('div',{'class':'Datetime ArticleHeader-Date'}).text.split('-')[0])
                    article['date_publish'] = date
                except:
                    try:
                        date_text = soup.find('meta', property = "article:published_time")['content']
                        date = dateparser.parse(date_text).replace(tzinfo = None)
                        article['date_publish'] = date  
                    except:
                        date_text = None
                        article['date_publish'] = None  
                print("newsplease date: ", article['date_publish'])

            if not article['date_publish']:
                try: 
                    maintext = soup.find_all('p', {'class':'font--secondary'})
                    maintext = ''
                    for i in soup.find_all('p', {'class':'font--secondary'}):
                        maintext += i.text
                    article['maintext'] = maintext
                except:
                    try:
                        maintext = soup.find('div', {'class': "sart-intro"}).text
                        article['maintext'] = maintext
                        
                    except: 
                        maintext = None
                        article['maintext']  = None
            try:
                maintetx = ''
                for i in soup.find_all('p' ,{'class' : 'font--secondary'}):
                    maintetx += i.text
                article['maintext'] = maintetx
            except:
                article['maintext'] = article['maintext'] 
            print("newsplease maintext: ", article['maintext'][:50])
 
            # if not article['maintext']:
                
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
