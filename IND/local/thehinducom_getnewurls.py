"""
Created on Nov 7, 2022 

Craated by Hanling Su
"""

# Packages:

from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from datetime import datetime
from pymongo.errors import DuplicateKeyError
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
import re
import json
import pandas as pd


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'thehindu.com'
sitemap_base = 'https://thehindu.com/sitemap/archive/all/'


final_count = 0
final_processed_url_count = 0
final_inserted_url_count =0

hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# USING CATEGORY
category = ['national', 'international', 'states', 'cities']
page_start = [150,90,2,1200]
page_end = [150,90,2, 1300]
base = 'https://www.thehindu.com/news/'
direct_URLs = []
for c, ps, pe in zip(category, page_start, page_end):
    for p in range(ps, pe):
        url = base + c + '/fragment/showmoredesked?page=' + str(p)

        print(url)
        req = requests.get(url, headers = hdr)
        soup = BeautifulSoup(req.content)

        for i in soup.find_all('h3', {'class' : 'title big'}):
            direct_URLs.append(i.find('a')['href'])
        print('Now collected',len(direct_URLs), 'URLs')

blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

final_result = direct_URLs.copy()
print('Total articles collected', len(final_result))

inserted_url_count = 0
processed_url_count = 0

for url in final_result:
    print(url)
    try:
        req = requests.get(url, headers = hdr)
        soup = BeautifulSoup(req.content)
        # time.sleep(1)
        article = NewsPlease.from_html(req.text, url=url).__dict__
        
        # add on some extras
        article['date_download']=datetime.now()
        article['download_via'] = "Direct2"
        article['source_domain'] = source


        print("newsplease title: ", article['title'])
        # fix date
        try:
            date = soup.find('meta', {'name' : 'publish-date'})['content']
            article['date_publish'] = dateparser.parse(date).replace(tzinfo = None)
        except:
            article['date_publish'] = article['date_publish'] 
        print("newsplease date: ", article['date_publish'])

        # fix maintext
        try:
            maintext = ''
            for i in soup.find('div', {'class' :'articleBody'}).find_all('p'):
                maintext += i.text
            article['maintext'] = maintext
        except:
            try:
                maintext = ''
                for i in soup.find('div', {'itemprop' :'articleBody'}).find_all('p'):
                    maintext += i.text
                article['maintext'] = maintext
            except:
                try:
                    article['maintext'] = soup.find('h2').text
                except:
                    article['maintext'] = article['maintext'] 

        if article['maintext']:
            print("newsplease maintext: ", article['maintext'][:50])

    except:
        print('Connection error, continue with next article...')
        continue

    
    

    # add to DB
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
            inserted_url_count += 1
            print("Inserted! in ", colname, " - number of urls so far: ", inserted_url_count)
        db['urls'].insert_one({'url': article['url']})
    except DuplicateKeyError:
        myquery = { "url": url, "source_domain" : source}
        db[colname].delete_one(myquery)
        db[colname].insert_one(article)
        pass
        print("DUPLICATE! UPDATED!")
        
    processed_url_count +=1    
    print('\n',processed_url_count, '/', len(final_result) , 'articles have been processed ...\n')

print("Done inserting ", inserted_url_count, " manually collected urls from ",  source, " into the db.")
    


# for year in range(2022, 2023):
#     year_str = str(year)

#     for month in range(11, 12):
#         if month < 10:
#             month_str = '0' + str(month)
#         else:
#             month_str = str(month)
        
#         for day in range(23, 31):
#             direct_URLs = []
#             if day < 10:
#                 day_str = '0' +str(day)
#             else:
#                 day_str = str(day)

            # USING SITEMAPS

            # sitemap = sitemap_base + year_str + month_str +  day_str +'_1.xml'
            # print(sitemap)
            # req = requests.get(sitemap, headers = hdr)
            # soup = BeautifulSoup(req.content)

            # for i in soup.find_all('loc'):
            #     direct_URLs.append(i.text)
            # print('Now collected',len(direct_URLs), 'URLs')

            # blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
            # blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
            # direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

            # final_result = direct_URLs.copy()
            # final_count += len(final_result)
            # print('Total articles collected', len(final_result))
            # sitemap = 'https://www.thehindu.com/sitemap/update/all.xml'


            # USING DAILY ARCHIVE
            # archive_url = 'https://www.thehindu.com/archive/web/' + year_str +'/' + month_str+'/' +  day_str+'/?page='
            # for p in range(30):
            #     sitemap = archive_url + str(p)

            #     print(sitemap)
            #     req = requests.get(sitemap, headers = hdr)
            #     soup = BeautifulSoup(req.content)

            #     for i in soup.find_all('div', {'class' : 'title'}):
            #         direct_URLs.append(i.find('a')['href'])
            #     print('Now collected',len(direct_URLs), 'URLs')

            #     blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
            #     blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
            #     direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

            #     final_result = direct_URLs.copy()
            #     final_count += len(final_result)
            #     print('Total articles collected', len(final_result))
            
#             inserted_url_count = 0
#             processed_url_count = 0

#             for url in final_result:
#                 print(url)
#                 try:
#                     req = requests.get(url, headers = hdr)
#                     soup = BeautifulSoup(req.content)
#                     # time.sleep(1)
#                     article = NewsPlease.from_html(req.text, url=url).__dict__
                    
#                     # add on some extras
#                     article['date_download']=datetime.now()
#                     article['download_via'] = "Direct2"
#                     article['source_domain'] = source

    
#                     print("newsplease title: ", article['title'])
#                     # fix date
#                     try:
#                         date = soup.find('meta', {'name' : 'publish-date'})['content']
#                         article['date_publish'] = dateparser.parse(date).replace(tzinfo = None)
#                     except:
#                         article['date_publish'] = article['date_publish'] 
#                     print("newsplease date: ", article['date_publish'])

#                     # fix maintext
#                     try:
#                         maintext = ''
#                         for i in soup.find('div', {'class' :'articleBody'}).find_all('p'):
#                             maintext += i.text
#                         article['maintext'] = maintext
#                     except:
#                         try:
#                             maintext = ''
#                             for i in soup.find('div', {'itemprop' :'articleBody'}).find_all('p'):
#                                 maintext += i.text
#                             article['maintext'] = maintext
#                         except:
#                             try:
#                                 article['maintext'] = soup.find('h2').text
#                             except:
#                                 article['maintext'] = article['maintext'] 

#                     if article['maintext']:
#                         print("newsplease maintext: ", article['maintext'][:50])

#                 except:
#                     print('Connection error, continue with next article...')
#                     continue

                
                
            
#                 # add to DB
#                 try:
#                     year = article['date_publish'].year
#                     month = article['date_publish'].month
#                     colname = f'articles-{year}-{month}'
                    
#                 except:
#                     colname = 'articles-nodate'
                
#                 # Inserting article into the db:
#                 try:
#                     db[colname].insert_one(article)
#                     # count:
#                     if colname != 'articles-nodate':
#                         inserted_url_count += 1
#                         print("Inserted! in ", colname, " - number of urls so far: ", inserted_url_count)
#                     db['urls'].insert_one({'url': article['url']})
#                 except DuplicateKeyError:
#                     myquery = { "url": url, "source_domain" : source}
#                     db[colname].delete_one(myquery)
#                     db[colname].insert_one(article)
#                     pass
#                     print("DUPLICATE! UPDATED!")
                    
#                 processed_url_count +=1    
#                 print('\n',processed_url_count, '/', len(final_result) , 'articles have been processed ...\n')

#                 final_inserted_url_count += inserted_url_count
#             final_processed_url_count += processed_url_count
    
#     print('\n',final_processed_url_count, '/', final_count , 'articles have been processed ...\n')

# print("Done inserting ", final_inserted_url_count, " manually collected urls from ",  source, " into the db.")
    
