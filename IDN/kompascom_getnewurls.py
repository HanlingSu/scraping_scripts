# Packages:
import re
from pymongo import MongoClient
from bs4 import BeautifulSoup
from dateparser.search import search_dates
import dateparser
import requests
from urllib.parse import quote_plus
from warnings import warn
from pymongo import MongoClient
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
from dotenv import load_dotenv
import pandas as pd


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []
source = 'kompas.com'


# category = ['nasional', 'regional', 'megapolitan', 'global' ]
# page_start = [1,1,100,1]
# page_end = [0,0,666,1]

# base = 'https://kolom.kompas.com/?source=navbar'

# for c, ps, pe in zip(category, page_start, page_end):
# for p in range(1, 357+1):
#     url = base + c + '&page=' +str(p)

#     hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
#     req = requests.get(url, headers = hdr)
#     soup = BeautifulSoup(req.content)
#     item = soup.find_all('h3', {'class' : 'article__title article__title--medium'})

#     for i in item:
#         direct_URLs.append(i.find('a')['href'])

#     print('Now scraped ', len(direct_URLs), ' articles from previous sitemaps.')



for year in range(2024, 2025):
    year_str = str(year)
    for month in range(7, 8):
        direct_URLs = []
        if month < 10:
            month_str = '0' + str(month)
        else:
            month_str = str(month)
        print('Now scraping articles published in', year_str, month_str, '...')
        for day in range(1, 32):
            if day < 10:
                day_str= '0' + str(day)
            else:
                day_str = str(day)
            for page in range(1, 30):
                url = 'https://indeks.kompas.com/?site=news&date=' + year_str + '-' + month_str + '-' + day_str + '&page=' + str(page)
                hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
                try:
                    req = requests.get(url, headers = hdr)
                    soup = BeautifulSoup(req.content)
                    item = soup.find_all('a', {'class' : 'article-link'})
                    for i in item:
                        direct_URLs.append(i['href'])
                except:
                    pass
            print(url)
            print('Now scraped ', len(direct_URLs), ' articles from previous pages.')




# direct_URLs = [url for url in direct_URLs if 'https://megapolitan.kompas.com/' in url]

# d = [i for i in db['articles-nodate'].find(
    
#         {
#             'url': {'$regex' : 'https://megapolitan.kompas.com/.*'},
#             'source_domain' : 'kompas.com'
#         }
#     )]

# d1 = pd.DataFrame(d)
# direct_URLs = d1['url']



blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

final_result = sorted(list(set(direct_URLs)))
print(len(final_result))


url_count = 0
processed_url_count = 0


for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            header =  {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'} #header settings

            response = requests.get(url, headers=header)
            # process
            article = NewsPlease.from_html(response.text, url=url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            article['language'] = 'id'
            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser')

            if 'https://megapolitan.kompas.com' in url:
                #fix date
                try:
                    date =soup.find('meta', {'name' : 'content_PublishedDate'})['content'] 
                    article['date_publish'] = dateparser.parse(date).replace(tzinfo = None)
                except:
                    try:
                        date =soup.find('meta', property = 'article:published_time')['content']
                        article['date_publish'] = dateparser.parse(date)
                    except:
                        article['date_publish'] = None
                print("newsplease date: ", article['date_publish'])

                try:
                    title  = soup.find('h1').text
                    article['title'] = title
                except:
                    article['title'] =  article['title'] 
                print("newsplease title: ", article['title'])

                try:
                    maintext = soup.find('div', {'class' : 'read__content'}).text
                    article['maintext'] = maintext.strip()
                except:
                    soup.find_all('p')
                    maintext = ''
                    for i in soup.find_all('p'):
                        maintext += i.text
                    article['maintext'] = maintext.strip()
                if article['maintext'] :
                    article['maintext'] = article['maintext'].replace('KOMPAS.com', '').replace('-', '', 1).strip()
                    print("newsplease maintext: ", article['maintext'][:50])

            else:
                # title has no problem
                
                print("newsplease title: ", article['title'])
                
            
                # fix main text
                try:
                    soup.find('div', {'class' : 'read__content'}).find_all('p')
                    maintext = ''
                    for i in soup.find('div', {'class' : 'read__content'}).find_all('p'):
                        maintext += i.text.replace('KOMPAS.com', '').strip()
                        article['maintext'] = maintext

                except:
                    maintext = None
                    article['maintext'] = maintext
                if article['maintext']:
                    print("newsplease maintext: ", article['maintext'][:50])
                
                #fix date
                try:
                    date = soup.find('meta', {'name' : 'content_PublishedDate'})['content']
                    article['date_publish'] = dateparser.parse(date)
                except:
                    try:
                        date = soup.find('meta', property = 'article:published_time')['content']
                        article['date_publish'] = dateparser.parse(date).replace(tzinfo = None)
                    except:
                        article['date_publish'] = None
                print("newsplease date: ", article['date_publish'])


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
                    db['articles-nodate'].delete_many({'url' : url})

                    print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                db['urls'].insert_one({'url': article['url']})
            except DuplicateKeyError:
                db['articles-nodate'].delete_many({'url' : url})

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
