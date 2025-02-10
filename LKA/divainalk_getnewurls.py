# Packages:
from typing import final
from unicodedata import category
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import dateparser
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import re
import json
import time

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
direct_URLs = []
source = 'divaina.lk'

# sitemap_base = 'https://divaina.lk/wp-sitemap-posts-post-'
# for i in range(18, 22):
#     sitemap = sitemap_base + str(i) +'.xml'
#     print(sitemap)
#     hdr = {'User-Agent': 'Mozilla/5.0'}
#     req = requests.get(sitemap, headers = hdr)
#     soup = BeautifulSoup(req.content)
#     items = soup.find_all('loc')
#     for item in items:
#         direct_URLs.append(item.text)
        
#     print('Now collected ', len(direct_URLs), 'articles from previous pages...')


categories= ['main-news', 'vigasa-puwath', 'pradeshiya-puvath']
                #main       immediate news  local news          
page_start = [1, 79, 1]
page_end = [0, 100, 0 ]
# only change before each update

url_count = 0
processed_url_count = 0
final_result_len = 0
for c, ps, pe in zip(categories, page_start, page_end):
    for i in range(ps, pe+1):
        direct_URLs = []
        link = 'https://divaina.lk/category/' + c + '/page/' + str(i)
        print(link)

        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = requests.get(link, headers = hdr)
        soup = BeautifulSoup(req.content)
        items = soup.find('div', {'id' : 'tdi_64'}).find_all('h3', {'class' : 'entry-title td-module-title'})
        for item in items:
            direct_URLs.append(item.find('a')['href'])
        direct_URLs = list(set(direct_URLs))
   
        print('Now collected ', len(direct_URLs), 'articles from previous pages...')
    

        final_result = direct_URLs.copy()
        print(len(final_result))
        final_result_len += len(final_result)
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
                    article['language'] = 'si'
                    print("newsplease date: ", article['date_publish'])
                    print("newsplease title: ", article['title'])
                    # print("newsplease maintext: ", article['maintext'][:50])
        
                    ## Fixing Date:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # try:
                    #     article_title = soup.find("meta", property = 'og:title')['content']
                    #     article['title']  = article_title 
                    # except:
                    #     article_title = None
                    #     article['title']  = None
                    
                    # if not article['date_publish']:
                    #     try:
                    #         date = dateparser.parse(soup.find('div',{'class':'Datetime ArticleHeader-Date'}).text.split('-')[0])
                    #         article['date_publish'] = date
                    #     except:
                    #         try:
                    #             date_text = soup.find('meta', property = "article:published_time")['content']
                    #             date = dateparser.parse(date_text).replace(tzinfo = None)
                    #             article['date_publish'] = date  
                    #         except:
                    #             date_text = None
                    #             article['date_publish'] = None  
                    #     print("newsplease date: ", article['date_publish'])

                    if not article['maintext']:
                        try: 
                            maintext = soup.find('div', {'class': "td-post-content tagdiv-type"}).text.strip()
                            article['maintext'] = maintext
                        except:
                            try:
                                soup.find('div', {'class' : 'td-post-content tagdiv-type'}).find_all('p')
                                maintext = ''
                                for i in soup.find('div', {'class' : 'td-post-content tagdiv-type'}).find_all('p'):
                                    maintext += i.text
                                article['maintext'] = maintext.strip()
                            except:
                                maintext = None
                                article['maintext']  = None
                    
                    if article['maintext']:
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
                        #myquery = { "url": final_url, "source_domain" : 'web.archive.org'}
                        #db[colname].delete_one(myquery)
                        # Inserting article into the db:
                        db[colname].insert_one(article)
                        # count:
                        if colname!= 'articles-nodate':
                            url_count = url_count + 1
                            print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                            db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        print("DUPLICATE! Not inserted.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
                processed_url_count += 1
                print('\n',processed_url_count, '/', final_result_len, 'articles have been processed ...\n')

            else:
                pass
        time.sleep(300)

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
