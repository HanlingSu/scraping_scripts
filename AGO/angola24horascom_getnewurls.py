
from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from random import randint, randrange
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
source = 'angola24horas.com'

documents = db.sources.find({'source_domain': source}, { 'source_domain':1, 'primary_location': 1, '_id': 0 })
for document in documents:
    primary_location = document['primary_location']

categories = ['politica', 'sociedade', 'economia', 'internacional', 'mais/mais-categorias/nacional', 'opiniao']
page_start = [0, 0, 0, 0, 0, 1]
page_end = [120, 0, 0, 0, 0, 0]
# 120, 240, 50, 20, 1
        # politicle, region, society, economics, world 
base = 'https://angola24horas.com/'

url_count = 0
processed_url_count = 0
len_final_result = 0

for c, ps, pe in zip(categories, page_start, page_end):
    direct_URLs = []

    for p in range(ps+1, pe+1, 6):
        link = base + c +'?start=' + str(p) 
        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
        req = requests.get(link, headers = hdr)
        soup = BeautifulSoup(req.content)
        item = soup.find_all('h3', {'class' : 'catItemTitle'})
        for i in item:
            url = i.find('a')['href']
            direct_URLs.append(url)

        print(len(direct_URLs))

    final_result =['https://angola24horas.com' + i for i in direct_URLs]
    len_final_result += len(final_result)
    print(len_final_result)


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
                print("newsplease maintext: ", article['maintext'][:50])
                        
                # custom parser
                soup = BeautifulSoup(response.content, 'html.parser')
                
            
    
                
                try:
                    year = article['date_publish'].year
                    month = article['date_publish'].month
                    if c == "opiniao":
                        print(primary_location)
                        colname = f'opinion-articles-{year}-{month}'
                        article['primary_location'] = primary_location

                    else:
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
            print('\n',processed_url_count, '/', len_final_result, 'articles have been processed ...\n')
        else:
            pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
