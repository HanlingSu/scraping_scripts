
from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from random import randint, randrange
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
from langdetect import detect


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []
# categories = ['Mundo', 'corrupcao', 'Crime', 'denuncia', 'Economia', 'politica', 'Sociedade']
# page_start = [1, 1, 1, 1, 1, 1, 1]
# page_end = [1, 1, 1, 1, 1, 1, 1]

categories = ['noticias']
page_start = [1, ]
page_end = [13]
# https://angola-online.net/noticias?page=20
# page_end = [2, 2, 9, 2, 10, 20, 20]


base = 'https://angola-online.net/'

for c, ps, pe in zip(categories, page_start, page_end):
    for p in range(ps, pe+1):
        link = base + c +'?page=' + str(p) 
        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
        req = requests.get(link, headers = hdr)
        soup = BeautifulSoup(req.content)
        item = soup.find_all('div', {'class' : 'content-timeline__detail__container'})
        for i in item:
            url = i.find('a')['href']
            direct_URLs.append(url)

        print(len(direct_URLs))

final_result =list(set(direct_URLs))
print(len(final_result))

url_count = 0
processed_url_count = 0
source = 'angola-online.net'
for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            header = hdr = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=header)
            # process
            article = NewsPlease.from_html(response.text, url=url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            
            # title has no problem
            print("newsplease title: ", article['title'])
            print("newsplease date: ",  article['date_publish'])
                      
            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser')
            
            try:
                maintext = soup.find('div', {'itemprop' :'articleBody'}).text.strip()
                article['maintext'] = maintext
            except:
                maintext = soup.find('div', {'itemprop' :'description'}).text.strip()
                article['maintext'] = maintext
            print("newsplease maintext: ", article['maintext'][:50])

            code =  detect(article['maintext'])
            article['language'] = code 
            print(article['language'] )

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
