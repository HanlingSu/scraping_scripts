# Packages:
import sys
sys.path.append('../')
import re
from pymongo import MongoClient
from urllib.parse import urlparse
from datetime import datetime
from pymongo.errors import DuplicateKeyError
import requests
#from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from bs4 import BeautifulSoup
# %pip install dateparser
import dateparser
import json
import pandas as pd

# db connection:
uri = 'mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true'
db = MongoClient(uri).ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

## NEED TO DEFINE SOURCE!
source = 'lesahel.org'


categories = ['politique', "societe", "dossier", "economie"]

page_start = [0, 0, 0, 0]
page_end = [12, 50, 1, 1 ]

direct_URLs = []
for c, ps, pe in zip(categories, page_start, page_end):
    for p in range(ps, pe+1):
        url = 'https://www.lesahel.org/category/'+ c + '/page/' + str(p)

        print("Extracting from ", url)

        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')
        try:
            for i in soup.find_all('h4'):
                direct_URLs.append(i.find('a')['href'])
        except:
            pass
            
        print('Now collected', len(direct_URLs), 'articles ... ')

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
                date = soup.find('meta', {'property' : "article:published_time"})['content']
                date = dateparser.parse(date).replace(tzinfo = None)
            except:
                try:
                    s = str(json.loads(soup.find('script',type="application/ld+json").string))
                    date = re.findall("'datePublished': '(.*)', 'dateModified", s)[0]
                    date = dateparser.parse(date).replace(tzinfo = None) 
                except:
                    try:
                        s = str(json.loads(soup.find('script',type="application/ld+json").string))
                        date = re.findall('"datePublished": "(.*)", "dateModified', s)[0]
                        date = dateparser.parse(date).replace(tzinfo = None)

                    except:
                        try:
                            s = str(soup.find_all('div',{'class':'date1'}))
                            date = re.findall('--></div>\n(.*)\n</div>', s)[0]
                            date = dateparser.parse(date).replace(tzinfo = None)
                        except:    
                            try:
                                ds = str(json.loads(soup.find('script',type="application/ld+json").string))
                                date = re.findall("'article_publication_date': '(.*)'", s)[0]
                                date = dateparser.parse(date).replace(tzinfo = None)
                            except:
                                try:
                                    date = '20'+re.findall("/20(.*)", url)[0][:5]
                                    date = dateparser.parse(date).replace(tzinfo = None)

                                except:
                                    date = None 
                                    print('Custom_parser: Empty date!')
            article['date_publish'] = date

            print("newsplease date: ", article['date_publish'])
            print("newsplease title: ", article['title'])

            try:
                maintext = ''
                for i in soup.find('div', {'class' :'entry-content read-details'}).find_all('p'):
                    maintext += i.text  
                article['maintext'] = maintext.strip()
            except:
                try:    
                    maintext = ''
                    for i in soup.find_all('p')[3:]:
                        maintext += i.text 
                    article['maintext'] = maintext.strip()
                except:
                    article['maintext'] = article['maintext'] 

            if  article['maintext']:
                print("newsplease maintext: ", article['maintext'][:50])
                   
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'articles-{year}-{month}'
                
            except:
                colname = 'articles-nodate'
            print(colname)
            # Inserting article into the db:
            try:
                db[colname].insert_one(article)
                # count:
                if colname != 'articles-nodate':
                    url_count = url_count + 1
                    print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                db['urls'].insert_one({'url': article['url']})
            except DuplicateKeyError:
                db[colname].delete_one({'url': url})
                db[colname].insert_one(article)

                print("DUPLICATE! Updated.")
                
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
