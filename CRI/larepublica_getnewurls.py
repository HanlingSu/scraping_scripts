
from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from random import randint, randrange
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import json

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []

sitemap_base = 'https://www.larepublica.net/sitemaps/'
source = 'larepublica.net'

# 96
for year in range(2024, 2025):
    for month in range(11, 13):
        if month < 10:
            month_str = '0' + str(month)
        else:
            month_str = str(month)
        
        sitemap = sitemap_base + str(year) +'/' + month_str + '.xml'
        
        print(sitemap)
        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
        req = requests.get(sitemap, headers = hdr)
        soup = BeautifulSoup(req.content)
        item = soup.find_all('loc')
        for i in item:
            url = i.text
            direct_URLs.append(url)
        print(len(direct_URLs))
print(len(direct_URLs))


final_result = direct_URLs.copy()
print(len(final_result))

url_count = 0
processed_url_count = 0

for url in final_result[::-1]:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            header ={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'} #header settings

            response = requests.get(url, headers=header)
            # process
            article = NewsPlease.from_html(response.text, url=url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            
            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser')
        
            # title has no problem

            try:
                date = json.loads(soup.find('script', {'type' : "application/ld+json"}).contents[0], strict=False)['datePublished']
                article['date_publish'] = dateparser.parse(date)
            except:
                article['date_publish'] = article['date_publish']
            print("newsplease date: ",  article['date_publish'])


            try:
                maintext = ""
                for i in soup.find('div', {'class' : 'is-size-4 has-text-black has-text-justified article eplInternal'}).find_all('p', {'class' : None}):
                    maintext += i.text
                article['maintext'] = maintext.strip()
            except:
                article['maintext'] = article['maintext']

            # blacklist by category:
            try:
                category = soup.find('div', {'class' : 'column is-8 column-padding-right'}).find('a').text.strip()
            except:
                category = 'News'
            print(category)

            if category in ['NOTA DE TANO', 'MAGAZINE', 'ACCIÓN', 'SUPLEMENTOS']:
                article['date_publish'] = None
                article['maintext'] = ""
                article['title'] = 'From uninterested sections'


            print("newsplease title: ", article['title'])
            print("newsplease maintext: ", article['maintext'][:50])
                      

            
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                if category in ['READERS FORUM', 'FORO DE LECTORES']:
                    colname = f'opinion-articles-{year}-{month}'
                    article['primary_location'] = 'CRI'
                else:
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
                # myquery = { "url": url, "source_domain" : source}
                # db[colname].delete_one(myquery)
                # db[colname].insert_one(article)
                print("DUPLICATE! PASS.")
                pass
                
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')
    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
