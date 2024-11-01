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
import json
# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []
source = 'correiodabeiraserra.com'

# sitemap
# sitemap_base = 'https://www.correiodabeiraserra.com/post-sitemap'

# for i in range(1, 3):
#     sitemap = sitemap_base + str(i) + '.xml'
#     # print(sitemap)
#     hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
#     req = requests.get(sitemap, headers = hdr)
#     soup = BeautifulSoup(req.content)
#     item = soup.find_all('loc')

#     for i in item:
#         direct_URLs.append(i.text)


#     print('Now scraped ', len(direct_URLs), ' articles from previous pages.')

# final_result = direct_URLs.copy()
# print(len(final_result))

# # category
# base = 'https://www.correiodabeiraserra.com/category/'
# category =[ 'sociedade', 'nacional', 'mundo', 'politica-2', 'economia']
# page_start = [1,1,1,1, 1]
# page_end = [1,1,1,1, 1]

# # page_end = [2, 10, 4, 10, 10 ]

# for c, ps, pe in zip(category, page_start, page_end):
#     for p in range(ps, pe+1):
#         url = base + c + '/page/' + str(p)
#         print(url)
#         hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
#         req = requests.get(url, headers = hdr)
#         soup = BeautifulSoup(req.content)
#         item = soup.find_all('h2', {'class' : 'post-box-title' })
#         for i in item:
#             direct_URLs.append(i.find('a')['href'])
#         print('Now scraped ', len(direct_URLs), ' articles from previous pages.')


# all pages
base = 'https://correiodabeiraserra.sapo.pt/category/ultimas/page/'
for i in range(1, 41):
    url = base  +  str(i)
    print(url)
    hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    req = requests.get(url, headers = hdr)
    soup = BeautifulSoup(req.content)
    item = soup.find_all('h2', {'class' : 'post-box-title' })
    for i in item:
        direct_URLs.append(i.find('a')['href'])
    print('Now scraped ', len(direct_URLs), ' articles from previous pages.')


final_result = direct_URLs.copy()
print(len(final_result))

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

            
            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser')

            # blacklist 
            try:
                category = soup.find('span', {'class' : 'post-cats'}).text
            except:
                category = 'News'
            
            blacklist = ['Desporto', 'Opinião', 'Cultura']

            if any(cate in category for cate in blacklist):
                article['title'] = 'From uninterested category'
                article['date_publish'] = None
                article['maintext'] = None
                print(article['title'], category)
            else:
                
                #date parser
                try:
                    date = json.loads(soup.find('script', type = 'application/ld+json').contents[0])['@graph'][3]['datePublished']
                    article['date_publish'] = dateparser.parse(date)
                    
                except:
                    date = soup.find('span', {'class': 'tie-date'}).text
                    article['date_publish'] = dateparser.parse(date)
                # main text paser
                try:
                    soup.find('div', {'class': 'entry'}).find_all('p', {'class' : None})
                    maintext = ''
                    for i in soup.find('div', {'class': 'entry'}).find_all('p', {'class' : None}):
                        maintext += i.text
                    article['maintext'] =maintext
                except:
                    soup.find_all('p', {'class' : None})
                    maintext = ''
                    for i in soup.find_all('p', {'class' : None}):
                        maintext += i.text
                    article['maintext'] =maintext

                print("newsplease date: ", article['date_publish'])
                print("newsplease title: ", article['title'])
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
