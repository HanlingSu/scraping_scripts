# Packages:
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import dateparser
import pandas as pd
    
# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p


# direct_URLs = []
# base = 'https://mb.com.ph/wp-sitemap-posts-post-'
# page_start = 164
# page_end = 165
# for i in range(page_start, page_end+1):
#     sitemap = base + str(i) + '.xml'
#     hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
#     req = requests.get(sitemap, headers = hdr)
#     soup = BeautifulSoup(req.content)
#     item = soup.find_all('loc')
#     for i in item:
#         direct_URLs.append(i.text)

#     print(len(direct_URLs))

# final_result = direct_URLs.copy()

final_result = pd.read_csv('Downloads/peace-machine/peacemachine/getnewurls/PHL/mbcomph.csv')['0']
print(len(final_result))

url_count = 0
processed_url_count = 0
source = 'mb.com.ph'

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
                 
            
            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser')
           
            category = []
            for c in soup.find_all("meta", {"property":"article:section"}):
                category.append(c['content'])

            uninterested_categories = ['Sports', 'Fashion + Beauty', 'Arts + Culture', 'Life + Leisure', 'Home + Design',  'Opinion-Editorial', \
            'Opinion', 'Editorial', 'Celebrities', 'Food', 'Entertainment', 'Other Sports', 'Basketball', \
            'Volleyball', 'Golf', 'Boxing', 'Lifestyle']
            if any(item in category for item in uninterested_categories):
                # None info for non related news
                article['title']  = 'From uninterested Categories'
                article['date_publish'] = None
                print('\n', article['title'])
                print(category)

            else:
                try:
                    title = soup.find('meta', {'property' : 'og:title'})['content']
                    article['title'] = title
                except:
                    title = soup.find('h1').text
                    article['title'] = title

                try:
                    date = soup.find('span', {'class'  : 'mb-font-article-date'}).text
                    article['date_publish']  = dateparser.parse(date)
                except:
                    article['date_publish'] = article['date_publish'] 
            print("newsplease title: ", article['title'])
            print("newsplease date: ", article['date_publish'])
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
                db[colname].delete_one({ "url": article['url']})
                db[colname].insert_one(article)
                pass
                print("DUPLICATE! UPDATED.")
                
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
