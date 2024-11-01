
from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from random import randint, randrange
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import re
import pandas as pd
import json

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p



direct_URLs = []
sitemap = 'https://turan.az/storage/sitemap/az/sitemap_index_0.xml'
print(sitemap  )
hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

req = requests.get(sitemap, headers = hdr)
soup = BeautifulSoup(req.content)
item = soup.find_all('loc')
for j in item:
    url = j.text
    direct_URLs.append(url)
    # year_month = str(year) +'/10'
    # if year_month in url:
    #     direct_URLs.append(url)

print(len(direct_URLs))

# direct_URLs = pd.read_csv("Downloads/peace-machine/peacemachine/getnewurls/AZE/turan.csv")['0']
final_result = direct_URLs.copy()
print(len(final_result))

url_count = 0
processed_url_count = 0
source = 'turan.az'

for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            # header = hdr = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=header)
            # process
            article = NewsPlease.from_html(response.text, url=url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            
                    
            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser')

            month_dict = {
                'Yanvar':'January'  ,
                'Fevral':'February',
                'Mart':'March',
                'Aprel':'April',
                'May':'May',
                'İyun':'June',
                'İyul':'July',
                'Avqust':'August',
                'Sentyabr':'September',
                'Oktyab':'October',
                'Noyabr':'November',
                'Dekabr':'December'
            }

            # date
            
            try:
                date = soup.find('meta', {'name' : "og:article:published_time"})['content']
                article['date_publish'] = dateparser.parse(date)
            except:
                try:
                    d = soup.find('div', {'class' : 'col-md-6'}).text.strip().split('\n')[1].strip()
                    # print(month)
                    # month_new = month_dict[month]
                    # print(month_new)
                    # date = date.replace(month, month_new)     
                    article['date_publish'] = dateparser.parse(d)

                except:
                    date = json.loads(soup.find('script', {'type' : "application/ld+json"}).contents[0], strict=False)['datePublished']
                    article['date_publish'] = dateparser.parse(date)
                
            print("newsplease date: ",  article['date_publish'])
            
            # title
            if not  article['title']:
                try:
                    title = soup.find('h1').text
                    article['title'] = title.strip()
                except:
                    article['title'] = article['title'] 
            print("newsplease title: ", article['title'])
            
            if not article['maintext']:
                try:
                    maintext = soup.find('div', {'class' : 'post--content some-class-name2'}).text.strip()
                    article['maintext'] = maintext.split('Turan: ',1)[-1]
                except:
                    soup.find_all('p')
                    maintext = ''
                    for i in soup.find_all('p'):
                        maintext += i.text
                    article['maintext'] = maintext.strip().split('Turan: ',1)[-1]
                    
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
