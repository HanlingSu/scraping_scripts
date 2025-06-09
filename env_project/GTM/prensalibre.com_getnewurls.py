
# Packages:
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease


hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'env_prensalibre.com'

direct_URLs = []

for p in range(1, 18):
    link = 'https://www.prensalibre.com/tema/medio-ambiente/page/' + str(p) 
    print("Getting urls from: ",link)
    response = requests.get(link, verify=False)

    soup = BeautifulSoup(response.content)
    for i in soup.find_all('div', {'class' : 'mt-lg-0 cover-section__temas__container module__card story-xs story'}):
        try:
            direct_URLs.append(i.find('a')['href'])
        except:
            pass
    print('Now scraped ', len(direct_URLs), 'articles from previous months ... ')


print('There are ', len(direct_URLs), 'urls')


final_result = direct_URLs.copy()


print('The total count of final result is: ', len(final_result))

url_count = 0
processed_url_count = 0
for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            # process
            response = requests.get(url, verify=False)
            soup = BeautifulSoup(response.content)
            article = NewsPlease.from_html(response.text, url=url).__dict__

            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            article['url'] = url
            article['environmental'] = True
            
            print("newsplease date: ", article['date_publish'])
            print("newsplease title: ", article['title'])
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
                # myquery = { "url": final_url, "source_domain" : 'web.archive.org'}
                # db[colname].delete_one(myquery)
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
