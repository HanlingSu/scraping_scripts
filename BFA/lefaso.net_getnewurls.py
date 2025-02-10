# Packages:
from pymongo import MongoClient

from bs4 import BeautifulSoup
from newspaper import Article
import requests

from pymongo import MongoClient
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import dateparser

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

source = 'lefaso.net'

direct_URLs = []

# 127314
start = 133572
end =  135426
processed_url_count = 0
url_count = 0
final_result = end-start
for i in range(start, end +1):
    url = 'https://lefaso.net/spip.php?article' + str(i) 

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
            try:
                category = soup.find('div', {'id' : 'hierarchie'}).text.split('>')[-1].strip()
            except:
                category = 'News'
            print(category)
            if category in ['Sport' ,'Culture', 'Multimédia' ]:
                pass
            else:
                try:
                    date = soup.find('div', {'style' : 'width:100%'}).find('p').text.split(' ', 3)[-1].replace(' à ', ' ').replace('h', ':').replace('min', '')
                    article['date_publish'] = dateparser.parse(date)
                except:
                    article['date_publish'] = article['date_publish'] 

                print("newsplease date: ", article['date_publish'])
                print("newsplease title: ", article['title'])
                print("newsplease maintext: ", article['maintext'][:50])                    
                
                
                try:
                    year = article['date_publish'].year
                    month = article['date_publish'].month
                    if category == 'Opinions':
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
                    if colname !=  'articles-nodate':
                        url_count = url_count + 1
                        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                    db['urls'].insert_one({'url': article['url']})
                except DuplicateKeyError:
                    print("DUPLICATE! Not inserted.")
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', final_result, 'articles have been processed ...\n')

    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
