
from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from random import randint, randrange
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import langid
import cloudscraper
import gzip


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []

sitemap_base = 'https://www.echaab.dz/post-sitemap'

for i in range(60, 65):
    sitemap = sitemap_base + str(i) + '.xml'
    print(sitemap  )
    hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
    response = requests.get(sitemap, headers={'Accept-Encoding': 'identity'})
    soup = BeautifulSoup(response.content)
    item = soup.find_all('loc')
    for i in item:
        url = i.text
        direct_URLs.append(url)

    print(len(direct_URLs))

final_result = direct_URLs.copy()
final_result = final_result[::-1]
print(len(final_result))

url_count = 0
processed_url_count = 0
source = 'echaab.dz'

for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        
        flag = True
        while flag:
            try:
                response = requests.get(url, headers={'Accept-Encoding': 'identity'})
                soup = BeautifulSoup(response.content)
                article = NewsPlease.from_html(response.text, url=url).__dict__
            except:
                pass
            
            if article:
                flag = False
                
       
            
                # add on some extras
        try:
            category = []
            for i in soup.find_all('a', {'rel' : 'category tag'}):
                category.append(i.text)
        except:
            category = ['News']
                #  sports, culture, health, community, science and tech, fake news
        if  any(x in ['إقتصاد', 'ثقافة', 'صحة', 'مجتمع', 'علوم وتكنولوجيا', 'فايك نيوز'] for x in category):
            print("From uninterested category", category)
        else:
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source

            # title has no problem
            print("newsplease title: ", article['title'])
            print("newsplease date: ",  article['date_publish'])
            if not  article['maintext']:
                try:
                    maintext = soup.find('div', {'class' : 'content-inner'}).text       
                    article['maintext'] = maintext
                except:
                    article['maintext'] = article['maintext']
            if article['maintext']:       
                print("newsplease maintext: ", article['maintext'][:50])
            
            language, _ = langid.classify(article['maintext'])
            article['language'] = language
            print(article['language'] )

            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                if 'رأي' in category:
                    colname = f'opinion-articles-{year}-{month}'
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
                
            except:
#                 pass
                myquery = { "url": url, "source_domain" : source}
                db[colname].delete_one(myquery)
                db[f'opinion-articles-{year}-{month}'].delete_one(myquery)
                db[f'articles-{year}-{month}'].delete_one(myquery)
                
                db[colname].insert_one(article)
                print("DUPLICATE! Pass.")
                

        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')
    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
