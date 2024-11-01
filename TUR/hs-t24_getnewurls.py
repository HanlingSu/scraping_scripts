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

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


base = 'https://media-cdn.t24.com.tr/media/sitemaps/sitemap-'

source = 't24.com.tr'

direct_URLs = []

for year in range(2023, 2024):
    for month in range(2, 3):
        if month <10:
            strmonth = '0' + str(month)
        else:
            strmonth = str(month)
        for day in range(1, 2):
            
            if day <10:
                strday = '0' + str(day)
            else:
                strday = str(day)
        
            sitemapurl = base + str(year) + strmonth + strday +'.xml'
            print(sitemapurl)   
            reqs = requests.get(sitemapurl, headers=headers)
            soup = BeautifulSoup(reqs.text, 'html.parser')
            for link in soup.find_all('loc'):
                direct_URLs.append(link.text)
        print('Now collected', len(direct_URLs), 'articles ... ')

# blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
# blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
# direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

final_result = list(set(direct_URLs))
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
            print("newsplease title: ", article['title'])
            
            soup = BeautifulSoup(response.content, 'html.parser')

            try:
                date = json.loads(soup.find('script', type = 'application/ld+json').contents[0], strict=False)[0]['datePublished']
                article['date_publish'] = dateparser.parse(date).replace(tzinfo = None)
            except:
                try:
                    date = json.loads(soup.find('script', type = 'application/ld+json').contents[0], strict=False)[0]['datePublished']
                    article['date_publish'] = dateparser.parse(date).replace(tzinfo = None)
                except:
                    article['date_publish'] = article['date_publish'] 
            print("newsplease date: ", article['date_publish'])

            # Get Highlighted Text:
            try:
                highlighted_text = soup.find('h2').text.strip()
                if highlighted_text == '':
                    highlighted_text = None         
            except:
                highlighted_text = None

            # Get Main Text:
            try:
                contains_maintext = soup.find("div", {"class":"_1NMxy"})
                maintext = contains_maintext.text.strip()
                
            except: 
                soup.find_all('p')
                maintext = ''
                for i in soup.find_all('p'):
                    maintext += i.text
                maintext = maintext.strip()

            try:
                combined_text = highlighted_text + '. '+ maintext
                article['maintext'] = combined_text  
            except:
                combined_text = maintext
                article['maintext'] = combined_text
           
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
                myquery = { "url": url}
                db[colname].delete_one(myquery)
                # Inserting article into the db:
                db[colname].insert_one(article)
                    
                print("DUPLICATE! Updated!")

                # print("DUPLICATE! Not inserted.")
                pass
                
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
    else:
        pass
    processed_url_count += 1
                    
    print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')
                    
print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
