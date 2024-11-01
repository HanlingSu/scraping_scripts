
from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from random import randint, randrange
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import json
import pandas as pd
from time import sleep


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

urls = pd.read_csv('/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/PER/ojopublico_finalURLs.csv')

sitemap_base = 'https://ojo-publico.com/sitemap.xml?page='


# direct_URLs = []
# for i in range(1, 3):
#     sitemap = sitemap_base + str(i)
#     print(sitemap  )
#     hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
#      #header settings
#     req = requests.get(sitemap, headers = hdr)
#     soup = BeautifulSoup(req.content)
#     item = soup.find_all('loc')
#     for i in item:
#         url = i.text
#         direct_URLs.append(url)

#     print(len(direct_URLs))

# urls = direct_URLs.copy()



url_count = 0
processed_url_count = 0
source = 'ojo-publico.com'
for url in urls['url']:
#for url in urls:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            response = requests.get(url, headers=header)
            # process
            article = NewsPlease.from_html(response.text, url=url).__dict__
            soup = BeautifulSoup(response.content, 'html.parser')

            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
           
            try:
                title = soup.find('h1', {'class': 'article__title no-margin-top'}).text
                article['title'] = title

            except:
                try:
                    title = soup.find('h1', {'class' : 'story__heading'}).text
                    article['title'] = title
                except:
                    pass

            print("newsplease title: ", article['title'])

            ## highlighted section + maintext
            try:
                highlighted_section = soup.find('p', {'class': 'article__summary'}).text
                maintext = soup.find('div', {'property': 'schema:text'}).text
                fulltext = highlighted_section + ' ' + maintext

            except:
                try:
                    maintext = soup.find('div', {'property': 'schema:text'}).text
                    fulltext = maintext
                except:
                    fulltext = article['maintext']


            article['maintext'] = fulltext.strip()
               
            print("newsplease maintext: ", article['maintext'][:50])
            
                      
            # custom parser

            try:
                date = soup.find('span', {'class': 'article__info-text article__info-date d-none d-lg-inline'}).text
                article['date_publish'] = dateparser.parse(date)

            except:

                try:
                    date = soup.find('span', {'class' : 'date'}).text
                    article['date_publish'] = dateparser.parse(date)
                except:

                    try:
                        date = soup.find('p', {'class' : 'author'}).find('span',{'class' : None}).text

                    except:
                        try:
                            date = json.loads(soup.find('script', type = 'application/ld+json').contents[0])['@graph'][0]['datePublished']
                            article['date_publish'] = dateparser.parse(date)
                        except:

                            try:

                                date = soup.find('span', {'class' : 'article__info-text article__info-date d-lg-none'}).text
                                article['date_publish'] = dateparser.parse(date)
                            except:
                                date = soup.find('div', {'class' : 'story__summary'}).text.split(':')[-1]
                                article['date_publish'] = dateparser.parse(date)
                
            print("newsplease date: ",  article['date_publish'])
            
            
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
                db[colname].delete_one( {'url' : url })
                db[colname].insert_one(article)
                pass
                print("DUPLICATE! Updated.")
                
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(urls), 'articles have been processed ...\n')
    else:
        pass

    sleep(randint(1,2))


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
