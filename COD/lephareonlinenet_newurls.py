
# Packages:
from typing import final
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import dateparser
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import re

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
direct_URLs = []

source = 'lephareonline.net'

category = ['nation', 'justice', 'politique', 'point-chaud', 'societe', 'economie-et-finances']
end_page = [1, 1, 1, 3, 3, 1]


base = 'https://lephareonline.net/category/' 
for c, ep in zip(category, end_page):
    for p in range(ep+1):
        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
        link = base  + c +'/page/' + str(p)
        print(link)
        req = requests.get(link, headers = hdr)
        soup = BeautifulSoup(req.content)
        item = soup.find_all('h2', {'class' : 'entry-title'})
        for j in item:
            direct_URLs.append(j.find('a')['href'])
        # print(direct_URLs)
        print('Now scraped ', len(direct_URLs), ' articles from previous pages.')


# base = 'https://www.lephareonline.net/?paged=' 
# for c, pe in zip(category, end_page):
#     for p in range(1, pe+1):
#         hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
#         link = base + str(p) + c 
#         print(link)
#         req = requests.get(link, headers = hdr)
#         soup = BeautifulSoup(req.content)
#         item = soup.find_all('div', {'class' : 'col-sm-6 col-xxl-4 post-col'})
#         for j in item:
#             direct_URLs.append(j.find('a')['href'])
#         # print(direct_URLs)
#         print('Now scraped ', len(direct_URLs), ' articles from previous pages.')

# for i in range(2172, 2800):
#     url = 'https://lephareonline.net/?p=' +str(i)
#     header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
#     # print(url)
#     try:
#         response = requests.get(url, headers=header)
#         soup = BeautifulSoup(response.content, 'html.parser')
#         link = soup.find('meta', {'property' : 'og:url'})['content']
       
#         print(link)

#         direct_URLs.append(link)
#     # print(direct_URLs)
#         print('Now scraped ', len(direct_URLs), ' articles from previous pages.')
#     except:
#         pass

# blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
# blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
# direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

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
            print("newsplease title: ", article['title'])
        
        
            soup = BeautifulSoup(response.content, 'html.parser')
            try:
                soup.find('div', {'class' : 'entry-content'}).find_all('p')
                maintext = ''
                for i in soup.find('div', {'class' : 'entry-content'}).find_all('p'):
                    maintext += i.text
                article['maintext']  = maintext
            except: 
                try:
                    maintext = soup.find('div', {'class' : 'entry-content'}).text
                    article['maintext']  = maintext
                except: 
                    maintext = None
                    article['maintext']  = maintext
            print("newsplease maintext: ", article['maintext'][:50])
            
            try:
                date = soup.find('header', {'class' : 'entry-header'}).find('div', {'class' : 'entry-meta'}).find('div', {'class' : 'date'}).text
                article['date_publish'] = dateparser.parse(date).replace(tzinfo= None)
            except:
                try:
                    date = soup.find('meta', property = 'article:published_time')['content']
                    article['date_publish'] = dateparser.parse(date).replace(tzinfo= None)
                    
                except:
                    date = None 
                    article['date_publish'] = date
            print("newsplease date: ", article['date_publish'])
            
            
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'articles-{year}-{month}'
                
            except:
                colname = 'articles-nodate'
            
            # Inserti ng article into the db:
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
