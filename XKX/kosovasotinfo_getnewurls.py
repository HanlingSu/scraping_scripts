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
# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'kosova-sot.info'

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

keywords = ['eshte', 'ishte', 'dhe', 'jane']
# keywords = ['ajo','kjo','ishte','mos','pastaj','para','tij','per','ata','jete','kam','nje','kjo','disa','ose','kishte','nje','mund','cila','tyre']
# keywords = ['madh','pse','duhet','reja','kur','saj','tani','pak']
page_start = [50,55,55,30]
# page_end = [35, 28, 280, 15]
# page_end = [40,30,30,90,30,40,15,15,35,10,40,40,20,45,50,40,45,30,70,30]
page_end = [50,55,55,30]

base = 'https://www.kosova-sot.info/kerko/?keyword='


direct_URLs = []

for ps, pe, k in zip(page_start, page_end, keywords):
    for i in range(ps, pe+1):
        link = base + k + '&faqe=' + str(i)
        reqs = requests.get(link, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        for i in soup.find_all('div', {'class' : 'col-lg-2 col-5'}):
            direct_URLs.append(i.find('a')['href'])
        
        # direct_URLs =list(set(direct_URLs))
        print(len(direct_URLs))

blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

final_result = list(set(direct_URLs))
final_result = ['https://www.kosova-sot.info' + i for i in final_result]

print(len(final_result))


processed_url_count = 0
url_count = 0
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
            article['language'] = "sq"
            
            print('newsplease date: ', article['date_publish'])
            print("newsplease title: ", article['title'])
#             print("newsplease maintext: ", article['maintext'][:50])

           
            soup = BeautifulSoup(response.content, 'html.parser')
        
            try:
                maintext = soup.find('div', {'class': 'news-content'}).text.strip()
                article['maintext'] = maintext

            except: 
                try:
                    soup.find('div', {'class': 'news-content'}).find_all('p')
                    maintext = ''
                    for i in soup.find('div', {'class': 'news-content'}).find_all('p'):
                        maintext += i.text.strip()
                    article['maintext'] = maintext
                except:
                    try:
                        soup.find('div', {'class' : 'left-side-news'}).find_all('p')
                        maintext = ''
                        for i in soup.find('div', {'class' : 'left-side-news'}).find_all('p'):
                            maintext += i.text.strip()
                        article['maintext'] = maintext
                    except:
                        maintext = None
                        article['maintext']  = maintext
            print("newsplease maintext: ", article['maintext'][:50])

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
