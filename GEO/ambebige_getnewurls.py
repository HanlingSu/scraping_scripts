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

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# sitemap = 'https://www.ambebi.ge/sitemaps/articles_latest.xml'
# reqs = requests.get(sitemap, headers=headers)
# soup = BeautifulSoup(reqs.text, 'html.parser')

# for link in soup.find_all('loc'):
#     direct_URLs.append(link.text)

base = 'https://www.ambebi.ge/category/'
direct_URLs = []

categories = ['politika', 'sazogadoeba', 'samartali', 'msoplio', 'samkhedro', 'semtxveva', 'ekonomika', 'conflicts', ]
page_start = [1, 1, 1, 1, 1, 1, 1, 1]
page_end = [30, 30, 8, 16, 4, 0, 1, 1]

for c, ps, pe in zip(categories, page_start, page_end):
    for p in range(ps, pe):
        url = base + c + '/archive/?page=' + str(p)
        print(url)
        reqs = requests.get(url, headers=header)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        for link in soup.find_all('a', {'itemprop':'url'}):
            direct_URLs.append(link['href'])

        print(len(direct_URLs))

direct_URLs = ['https://www.ambebi.ge' + i for i in direct_URLs]
final_result = list(set(direct_URLs))
print(len(final_result))

source = 'ambebi.ge'
url_count = 0
for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
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
                soup.find('div', {'class' : 'article_content'}).find_all('p')
                maintext = ''
                for i in soup.find('div', {'class' : 'article_content'}).find_all('p'):
                    maintext += i.text
                article['maintext']  = maintext.strip()
            except:
                try:
                    maintext = soup.find('div', {'class' : 'article_content'}).text.strip()
                    article['maintext']  = maintext
                except:
                    maintext = None
                    article['maintext']  = maintext
            if  article['maintext']:
                print("newsplease maintext: ", article['maintext'][:50])
            
            # fix date
            try:
                date = soup.find('div', {'class': "article_date"}).text
                article['date_publish'] = dateparser.parse(date, settings={'DATE_ORDER': 'DMY'})
            except:
                try:
                    date = soup.find('div', {'class': 'maintopnewsdate'}).time['datetime']
                    article['date_publish'] =  dateparser.parse(date)
                except: 
                    try:
                        date = soup.fin('time').text
                        article['date_publish'] = dateparser.parse(date, settings={'DATE_ORDER': 'DMY'})

                    except:
                        date = None 
                        article['date_publish'] = None
            print("newsplease date: ", article['date_publish'])
            
            # fix title
            try:
                article_title = soup.find('meta',property = "og:title")['content']
                article['title']  = article_title   
            except:
                try:
                    article_title = soup.find('title').text.split('|')[0]
                    article['title']  = article_title  
                except:
                    try:
                        article_title = soup.find('div', {'class' : "article_title sa"}).text
                        article['title']  = article_title  
                    except:
                        article_title = None
                        article['title']  = None
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
    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
