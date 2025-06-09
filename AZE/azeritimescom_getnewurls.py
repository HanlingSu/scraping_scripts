
from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from random import randint, randrange
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import pandas as pd

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []

# sitemap_base = 'https://azeritimes.com/wp-sitemap-posts-post-'

# sitemap_base = 'https://azeritimes.com/page/'
# for i in range(1, 280):
#     sitemap = sitemap_base + str(i) + '?s=+'
#     print(sitemap  )
#     hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
#     req = requests.get(sitemap, headers = hdr)
#     soup = BeautifulSoup(req.content)
#     item = soup.find_all('li', {'class' : 'mvp-blog-story-wrap left relative infinite-post'})
#     for i in item:
#         url = i.find('a')['href']
#         direct_URLs.append(url)

#     print(len(direct_URLs))


direct_URLs = pd.read_csv('Downloads/peace-machine/peacemachine/getnewurls/AZE/azeritimes.csv')

text = """ """

direct_URLs = text.split('\n')
final_result = direct_URLs.copy()
print(len(final_result))

url_count = 0
processed_url_count = 0
source = 'azeritimes.com'
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
                category = soup.find('span' , {'class' : 'mvp-post-cat left'}).text
            except:
                category = 'News'
            print(category)  
            if category in ['Entertainment']:
                article['title'] = 'From unintersted category'
                article['date_publish'] = None
                article['maintext'] =  None
            
            print("newsplease title: ", article['title'], category)

            try:
                date = soup.find('meta', {'property' : 'article:published_time'})['content']
            except:
                pass
            
            if article['date_publish'] != dateparser.parse(date):
                article['date_publish'] = dateparser.parse(date)
            else:
                pass
             
            print("newsplease date: ",  article['date_publish'])
            if not article['maintext']:
                try:
                    maintext = soup.find('div', {'id' : 'mvp-content-main'}).find('div', {'class' : 'theiaPostSlider_preloadedSlide'}).text
                    article['maintext'] = maintext.strip()
                except:
                    maintext = soup.find('div', {'class' : 'theiaPostSlider_preloadedSlide'}).find('p').text
                    article['maintext'] = maintext.strip()
                    
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
                db[colname].delete_one({'url' : article['url']})
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
