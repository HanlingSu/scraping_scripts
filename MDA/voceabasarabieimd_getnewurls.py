
from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from random import randint, randrange
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []
source = 'voceabasarabiei.md'

sitemap_base = 'https://voceabasarabiei.md/post-sitemap'

#13 last 100
for i in range(22, 23):
    sitemap = sitemap_base + str(i) + '.xml'
    print(sitemap  )
    hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
    req = requests.get(sitemap, headers = hdr)
    soup = BeautifulSoup(req.content)
    item = soup.find_all('loc')
    for i in item:
        url = i.text
        direct_URLs.append(url)

    print(len(direct_URLs))

final_result = direct_URLs.copy()[::-1]
print(len(final_result))

url_count = 0
processed_url_count = 0
for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            header = hdr = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=header)
            # process
            article = NewsPlease.from_html(response.text, url=url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            # title has no problem
                 
            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser')
            
            try:
                category = soup.find('div', {'class' : 'tdb-category td-fix-index'}).text
            except:
                category = 'News'
            print(category)
            if category in ['Cultură', 'FAKE NEWS', 'INTERVIURI']:
                article['title'] = 'From unintersted category'
                article['date_publish'] = None
                article['maintext'] =  None
            
            print("newsplease title: ", article['title'])
            print("newsplease date: ",  article['date_publish'])

            try:
                maintext = ''
                for i in soup.find('div', {'class' : 'td_block_wrap tdb_single_content tdi_90 td-pb-border-top td_block_template_1 td-post-content tagdiv-type'}).find_all('p'):
                    maintext += i.text
                article['maintext'] = maintext.strip()
            except:
                maintext = ''
                for i in soup.find_all('p'):
                    maintext += i.text
                article['maintext'] = maintext.strip()
                
            if article['maintext']:
                print("newsplease maintxtext: ", article['maintext'][:50])
                 
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
