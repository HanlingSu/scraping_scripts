# Packages:
from unicodedata import category
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import pandas as pd
import dateparser
# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []

source = 'acpcongo.com'

# base_list = []

# base = ['https://acpcongo.com/index.php/category/nation/page/', 'https://acpcongo.com/index.php/category/economie/page/', \
#         'https://acpcongo.com/index.php/category/province/page/', 'https://acpcongo.com/index.php/category/societe/page/', \
#         'https://acpcongo.com/index.php/category/anglais/page/', 'https://acpcongo.com/index.php/category/genre/page/', \
#         'https://acpcongo.com/index.php/category/international/page/', 'https://acpcongo.com/index.php/category/sante/page/', ]
        
# page_start = [73, 56, 123, 23, 101, 57, 43, 32]
# page_end = [95,71,165,31,130,71,55,42]
# # page = [1,1,1,1,1,1,1,1]
# for b, ps, pe in zip(base, page_start, page_end):
#     for i in range(ps, pe+1):
#         base_list.append(b + str(i) )

direct_URLs = pd.read_csv('/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/COD/acpcongo.csv')['0']

# print('Scraping from ', len(base_list), 'pages ... ')

# for base_link in base_list:
#     hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

#     req = requests.get(base_link, headers = hdr)
#     soup = BeautifulSoup(req.content)
#     item = soup.find_all('h2', {'class' : 'entry-title'})
#     for i in item:
#         direct_URLs.append(i.find('a')['href'])

#     print('Now scraped ', len(direct_URLs), ' articles from previous pages.')

final_result = list(set(direct_URLs))
print('Total number of urls found: ', len(final_result))


url_count = 0
processed_url_count = 0
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
            # title has no problem
         
            soup = BeautifulSoup(response.content, 'html.parser')

            try:
                date = soup.find('time', {'class': "entry-date updated td-module-date"})['datetime']
                article['date_publish'] = dateparser.parse(date)
            except:
                date = soup.find('time').text
                article['date_publish'] = dateparser.parse(date)
            print("newsplease date: ", article['date_publish'])
            
            print("newsplease title: ", article['title'])
            article['maintext'] = article['maintext'].split('.- ', 1)[-1]
            if not article['maintext']:
                try:
                    maintext = soup.find('div', {'class' : 'entry-content'}).text
                    article['maintext'] = maintext
                except:
                    soup.find('div', {'class' : 'entry-content'}).find_all('p')
                    maintext = ''
                    for i in soup.find('div', {'class' : 'entry-content'}).find_all('p'):
                        maintext += i.text
                    article['maintext'] = maintext
                
            if  article['maintext']:
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
