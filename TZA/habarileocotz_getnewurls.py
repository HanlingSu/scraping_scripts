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


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
direct_URLs = []
categories = ['tanzania', 'tahariri', 'uchumi', 'habari-kina', 'safu', 'jamii', 'kimataifa',  'afya']
            #  national,  edit,      economy,   detailed news, rows,   Society,  international, health

page_start = [1, 1, 1, 1, 1, 1, 1, 1]
page_end = [20, 1, 7, 8, 1, 20, 13, 14]
url = 'https://habarileo.co.tz/category/'

for c, ps, pe in zip(categories, page_start, page_end):
    for i in range(ps, pe+1):
        # mundo, nacionales, noticias-del-dia, espectaculos, ciencia
        link = url + c + '/page/' + str(i)
        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
        req = requests.get(link, headers = hdr)
        soup = BeautifulSoup(req.content)
        item = soup.find_all('div', {'class' :'entry-header-inner'})
        for i in item:
            direct_URLs.append(i.find('h2').find('a')['href'])

        print(len(direct_URLs))

final_result = list(set(direct_URLs))
print(len(final_result))

url_count = 0
processed_url_count = 0
source = 'habarileo.co.tz'
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
            # add language code
            article['language'] = 'sw'
            

            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # fix title
            try:
                article['title']  = soup.find("h1", {'class' : 'post-title entry-title'}).text 
            except:
                article['title']  = article['title']
            print("newsplease title: ", article['title'])
            
            # fix date
            try:
                date = soup.find("meta", {"property":"article:published_time"})['content']
                article['date_publish'] = dateparser.parse(date)
            except:
                try:
                    contains_date = soup.find("span", {"class":"date meta-item tie-icon"}).text
                    date = dateparser.parse(contains_date)
                    article['date_publish'] = date
                except:
                    article['date_publish'] = None  
            print("newsplease date: ",  article['date_publish'])
                    
            # fix main text
            try:
                soup.find('div', {'class' : 'entry-content entry clearfix'}).find_all('p')
                maintext = ''
                for i in soup.find('div', {'class' : 'entry-content entry clearfix'}).find_all('p'):
                    maintext += i.text
                article['maintext'] = maintext.strip()
            except:
                try:
                    maintext = soup.find('meta', {'property' : 'og:description'})['content'].strip()
                    article['maintext'] = maintext
                except:
                    article['maintext'] = article['maintext'] 
            if article['maintext']:
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
