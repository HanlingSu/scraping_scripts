# Packages:
from unicodedata import category
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

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'panorama.com.al'

direct_URLs = []

categories = ['politike', 'kronike', 'aktualitet', 'kosova', 'ekonomi', 'rajoni', 'bota-rajoni' ]
page_start = [1, 1, 1, 1, 1, 1, 1]
page_end = [55, 45, 20, 5, 7, 4, 45]
# page_start = [50, 35, 12, 8, 5, 50, 5]
# page_end = [70, 45, 18, 12, 10, 70, 10]

base = 'http://www.panorama.com.al/category/'
for c, p_s, p_e in zip(categories, page_start, page_end):
    for p in range(p_s, p_e+1):
        link = base + c + '/page/' + str(p)
        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
        req = requests.get(link, headers = hdr)
        soup = BeautifulSoup(req.content)
        item = soup.find_all('div', {'class' : 'item-details'})

        for i in item:
            direct_URLs.append(i.find('a')['href'])
        direct_URLs = list(set(direct_URLs))
        print('Now scraped ', len(direct_URLs), ' articles from previous pages.')



final_result = direct_URLs.copy()
final_result = list(set(final_result))

len(final_result)

url_count = 0

progress_count = 0
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
            print('cutsom parser title:', article['title'] )
            
            
            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser')
    
            # fix Main Text:

            try:

                soup.find('div', {'style' : 'float:left; width:500px'}).find_all('p')
                maintext = ''
                for i in soup.find('div', {'style' : 'float:left; width:500px'}).find_all('p'):
                    maintext += i.text
                article['maintext']  = maintext

            except:
                try:
                    soup.find('div', {'style' : 'float:left; width:500px'}).find_all('div')
                    maintext = ''
                    for i in soup.find('div', {'style' : 'float:left; width:500px'}).find_all('div'):
                        maintext += i.text
                    article['maintext']  = maintext
                except:
                    try:
                        soup.soup('div', {'class' : 'td-post-content td-pb-padding-side'}).find_all('p')
                        maintext = ''
                        for i in soup.find('div', {'class' : 'td-post-content td-pb-padding-side'}).find_all('p'):
                            maintext += i.text
                        article['maintext']  = maintext
                    except:          
                        article['maintext']  = article['maintext']
            print('custom parser maintext:', article['maintext'][:50])
                        
            # fix date:
            try:
                date = soup.find('div', {'class': "meta-info"}).text
                article['date_publish'] = dateparser.parse(date)
            except:
                date = None 
                article['date_publish'] = None
            print('custom parser date:', article['date_publish'])

            
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
                    print("\nInserted! in ", colname, " - number of urls so far: ", url_count)
                db['urls'].insert_one({'url': article['url']})
            except DuplicateKeyError:
                pass
                print("DUPLICATE! Not inserted.")
                
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        
        print('\n.............Now scraped ', progress_count, 'articles...........')
        if progress_count // 100 == 0:
            print('\n............. ', len(final_result) - progress_count, 'articles to go ...........')
        progress_count += 1
        print('\n',progress_count, '/', len(final_result), 'articles have been processed ...\n')

    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
