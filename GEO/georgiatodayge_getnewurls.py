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
import langid



# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# sitmeap link:
sitemap = 'https://georgiatoday.ge/post-sitemap12.xml'

# source domain
source = 'georgiatoday.ge'

direct_URLs = []


reqs = requests.get(sitemap, headers=headers)
soup = BeautifulSoup(reqs.text, 'html.parser')

for link in soup.find_all('loc'):
    direct_URLs.append(link.text)

print(len(direct_URLs))
final_result = direct_URLs.copy()

print(len(final_result))

url_count = 0
processed_url_count = 0 
for url in final_result[::-1]:
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
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # fix maintext
            try:
                maintext = soup.find('div', {'class' : 'content-inner'}).text
                article['maintext']  = maintext.strip()
            
            except:
                try:
                    soup.find('div', {'class':'news-data'}).find_all('div')
                    maintext = ''
                    for i in soup.find('div', {'class':'news-data'}).find_all('div'):
                        maintext += i.text
                    article['maintext']  = maintext.strip()
                except:
                    article['maintext']  = article['maintext'].strip()
            if  article['maintext']:
                print("newsplease maintext: ", article['maintext'][:50])

            # check language code
            language, confidence = langid.classify(article['maintext'])
            # print(language)
            if language != article['language']:
                article['language'] = language       
       
            print('newsplease language:', article['language'])

            # fix date
            try:
                date = soup.find('div', {'style' : 'padding:10px 0; color:#ccc;'}).text
                article['date_publish'] = dateparser.parse(date)
            except:
                try:
                    date = soup.find('div', {'class': 'jeg_meta_date'}).text
                    article['date_publish'] =  dateparser.parse(date)
                except: 
                    try:
                        date = soup.fin('meta', property = 'article:published_time')['content']
                        article['date_publish'] = dateparser.parse(date)
    
                    except:
                        article['date_publish'] = article['date_publish']
            if article['date_publish']:
                print("newsplease date: ", article['date_publish'])
            
            # fix title
            try:
                article_title = soup.find('h1').text
                article['title']  = article_title 
                
            except:
                try:
                    article_title = soup.find('title').text.split('-')[0]
                    article['title']  = article_title  
                except:
                    try: 
                        article_title = soup.find('meta',property = "og:title")['content']
                        article['title']  = article_title   
                    except:
                        article['title']  = article['title']
            if article['title']:
                print("newsplease title: ", article['title'])

            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'articles-{year}-{month}'
                #print(article)
            except:
                colname = 'articles-nodate'
            print("Collection: ", colname)
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