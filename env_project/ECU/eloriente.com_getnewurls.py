

# Packages:
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import pandas as pd

# db connection:
db = MongoClient(
    'mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'eloriente.com'

final_result = pd.read_csv("/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/env_project/ECU/eloriente.csv")['0']


print('There are ', len(final_result), 'urls')

url_count = 0
processed_url_count = 0
for url in final_result:
    if url:
        print(url, "FINE")
        # SCRAPING USING NEWSPLEASE:
        try:
            header = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            response = requests.get(url, verify=False)
            response.encoding = 'utf-8'

            soup = BeautifulSoup(response.content)
            # 
            article = NewsPlease.from_html(response.text, url=url).__dict__

            # add on some extras
            article['date_download'] = datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            article['environmental'] = True


            print("newsplease title: ", article['title'])

            try:
                date = json.loads(soup.find_all('script', {'type' : "application/ld+json"})[-1].contents[0], strict=False)['datePublished']
                article['date_publish'] = dateparser.parse(date, settings = {'DATE_ORDER' : 'DMY'})
            except:
                article['date_publish'] = article['date_publish'] 
            print("newsplease date: ", article['date_publish'] )

            
            try:
                maintext = json.loads(soup.find_all('script', {'type' : "application/ld+json"})[-1].contents[0], strict=False)['articleBody'].strip()
                article['maintext'] = maintext
            except:
                maintext = ''
                for i in soup.find('article',{'class':'col-lg-7 article'}).find_all('p'):
                    maintext += i.text
            print("newsplease maintext: ", article['maintext'][:50])


            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'articles-{year}-{month}'
                # print(article)
            except:
                colname = 'articles-nodate'
            # print("Collection: ", colname)
            try:
                db[colname].insert_one(article)
                # count:
                url_count = url_count + 1
                print("Inserted! in ", colname,
                      " - number of urls so far: ", url_count)
                db['urls'].insert_one({'url': article['url']})
            except DuplicateKeyError:
                db[colname].delete_one({'url':url}) 
                db[colname].insert_one(article)
                
                print("DUPLICATE! Not inserted.")
        except Exception as err:
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n', processed_url_count, '/', len(final_result),
              'articles have been processed ...\n')

    else:
        pass

print("Done inserting ", url_count,
      " manually collected urls from ",  source, " into the db.")
