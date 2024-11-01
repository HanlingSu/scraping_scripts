
from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from datetime import datetime
from pymongo.errors import DuplicateKeyError
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
import re
import pandas as pd

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

final_result = pd.read_csv('/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/PER/elcomerciope.csv')['0']
source = 'elcomercio.pe'

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

            print("newsplease date: ", article['date_publish'])

            print("newsplease title: ", article['title'])

            try:
                maintext = soup.find('p', {'class' : 'story-contents__font-paragraph story-contents--fade'}).text
                article['maintext'] = maintext
            except:
                try:
                    maintext = ''
                    for i in soup.find_all('p', {'itemprop' : 'description'})[:-2]:
                        maintext += i.text
                    article['maintext'] = maintext.strip()
                except:
                    if len(article['maintext'].split('\n')[:2]) >= 800:
                        article['maintext'] = article['maintext'].split('\n')[:2]
                    else:
                        article['maintext'] = article['maintext']
                    
            if article['maintext']:
                print("newsplease maintext: ", article['maintext'][:50])



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
#                 db[colname].delete_one({ "url": url, "source_domain" : source})
#                 db[colname].insert_one(article)

                print("DUPLICATE! Pass.")

        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
