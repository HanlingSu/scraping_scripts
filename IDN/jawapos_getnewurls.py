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
import cloudscraper

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)

hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'jawapos.com'


    # jawapos.com 
    # sitemap
# for month in range(12, 13):
#     direct_URLs = []
#     if month <10:
#         month_str = '0'+str(month)
#     else:
#         month_str = str(month)
    
#     url = 'https://www.jawapos.com/sitemap-pt-post-2023-' + month_str+'.xml'
#     print(url)
#     header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
#     response = requests.get(url, headers=header)
#     soup = BeautifulSoup(response.content, 'html.parser')
#     for i in soup.find_all('loc'):
#         direct_URLs.append(i.text)
#     print(len(direct_URLs))

# past sitemap content here

# direct_URLs = [ i.split(' ]]>')[0] for i in text.split('[CDATA[ ') if i.startswith('https://baliexpress.jawapos.com')]

# category

# date range
direct_URLs = []
base = 'https://www.jawapos.com/indeks-berita?daterange=14%20February%202025%20-%2028%20February%202025&page='
for p in range(1, 768+1):
    url = base +str(p)
    # print(url)
    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    response = requests.get(url, headers=header)
    soup = BeautifulSoup(scraper.get(url).text)
    for i in soup.find_all('h2', {'class' : 'latest__title'}):
        direct_URLs.append(i.find('a')['href'])
    print(len(direct_URLs))

# baliexpress.jawapos.com
# for month in range(12, 13):
#     direct_URLs = []
#     if month <10:
#         month_str = '0'+str(month)
#     else:
#         month_str = str(month)

#     for p in range(1, 100):
#         url = 'https://baliexpress.jawapos.com/sitemap-pt-post-p'+str(p)+'-2024-' + month_str+'.xml'
#         print(url)
#         header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
#         response = requests.get(url, headers=header)
#         soup = BeautifulSoup(response.content, 'html.parser')
#         for i in soup.find_all('loc'):
#             direct_URLs.append(i.text)
#         print(len(direct_URLs))


blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

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
            soup = BeautifulSoup(scraper.get(url).text)
            article = NewsPlease.from_html(scraper.get(url).text).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            article['url'] = url
            article['language'] = 'id'


            print("newsplease date: ", article['date_publish'])
            print("newsplease title: ", article['title'])
            # article['maintext'] = article['maintext'].replace('JawaPos.com', '')
            # article['maintext'] = article['maintext'].split('-', 1)[1]
            # print("newsplease maintext: ", article['maintext'][:50])

            ## Fixing Date:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            if not article['maintext']:
                try:
                    maintext = soup.find('div', {'itemprop' : 'articleBody'}).text

                except:
                    try:
                        maintext = soup.find('div', {'class' : 'content-article'}).text

                    except:
                        try:
                            maintext = soup.find('div', {'class' : 'content-article'}).text

                        except:
                            try:
                                maintext = soup.find('div', {'class' : 'content'}).text

                            except:
                                try:
                                    maintext = soup.find('div', {'class' : 'single-content'}).text
                    
                                except:
                                    try:
                                        soup.find('article').find_all('p')
                                        maintext = ''
                                        for i in soup.find('article').find_all('p'):
                                            maintext += i.text
                                        article['maintext'] = maintext.strip().replace('JawaPos.com', '')
                                    except:
                                        try:
                                            item = soup.find('div', {'class' : 'tdb-block-inner td-fix-index'}).find_all('p')
                                            maintext = ''
                                            for i in item:
                                                maintext += i.text
                                            article['maintext'] =  maintext.strip().replace('JawaPos.com', '')
                                        except:
                                            article['maintext']  = None

            if article['maintext']:   
                article['maintext'] =  article['maintext'].replace('JawaPos.com', '').strip().replace('-','', 1).strip()
                article['maintext'] =  article['maintext'].replace('BALI EXPRESS', '').strip().replace('-','', 1).strip()
                article['maintext'] =  article['maintext'].replace('BALIEXPRESS.ID', '').strip().replace('-','', 1).strip()
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
