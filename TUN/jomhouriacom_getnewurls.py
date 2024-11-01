# Packages:
from glob import escape
from json.tool import main
import re
from unicodedata import category
from pymongo import MongoClient

from bs4 import BeautifulSoup
import dateparser
import requests
import json
from pymongo import MongoClient
from urllib.parse import urlparse
from datetime import datetime
from pymongo.errors import DuplicateKeyError
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
direct_URLs = []

source = 'jomhouria.com'
hdr = {'User-Agent': 'Mozilla/5.0'} 

####### use sitemaps
# direct_URLs = []
# link = 'https://www.jomhoursia.com/sitemap.xml'
# hdr = {'User-Agent': 'Mozilla/5.0'}
# req = requests.get(link, headers = hdr)
# soup = BeautifulSoup(req.content)
# items = soup.find_all('loc')
# for item in items:
#     direct_URLs.append(item.text)
# print(len(direct_URLs))
# final_result = list(set(direct_URLs[-4000:]))


###### use categorized news
direct_URLs = []
categories = ['https://www.jomhouria.com/index.php?go=rub&id_rub=41&page=', 'https://www.jomhouria.com/index.php?go=rub&id_rub=32&page=', \
            'https://www.jomhouria.com/index.php?go=rub&id_rub=40&page=', 'https://www.jomhouria.com/index.php?go=rub&id_rub=43&page=']
                # economie
                # case and accident
                # national
                # internationa;

page_start = [1,1,1,1]
page_end = [14,30,85,25]
# page_end = [26,53,143,23]

for c, ps, pe in zip(categories, page_start, page_end):
    for p in range(ps, pe+1):
        link = c + str(p)
        req = requests.get(link, headers = hdr)
        soup = BeautifulSoup(req.content)
        items = soup.find_all('h2')
        for item in items:
            direct_URLs.append(item.find('a')['href'])
        print('Now scraped ', len(direct_URLs), 'URLs')
direct_URLs = ['https://www.jomhouria.com/' + i for i in direct_URLs]
final_result = list(set(direct_URLs))


month_dict = {
    'جانفي':'1',
    'فيفري':'2',
    'مارس':'3',
    'أفريل':'4',
    'ماي':'5',
    'جوان':'6',
    'جويلية':'7',
    'أوت':'8',
    'سبتمبر':'9',
    'أكتوبر':'10',
    'نوفمبر':'11',
    'ديسمبر':'12'
}

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
            article['language'] = 'ar'
            ## Fixing Date:
            soup = BeautifulSoup(response.content, 'html.parser')

            try:
                category = soup.find('div', {'id' : 'mainCol'}).find('a', {'href' : 'rub'}).text
            except:
                category = 'News'               
            
            if category in ['ثقافة', 'متفرّقات', 'رياضة' ]: # culture, sports, Miscellaneous
                print(category)
                article['date_publish'] = None
                article['title'] = 'From uninterested category'
                article['maintext'] = None
            
            # fix date

            try:
                date = soup.find('div', {'style' : 'float:right; margin-right:8px; padding-right:36px; width:200px; font-size:12px; font-weight:normal; background:url(images/cal.png) no-repeat top right'}).text
                date_list = date.strip().replace('نشر في ', '').replace('\xa0', '').split(' ')
                time = date_list[-1].strip('()')
                day = date_list[0]
                month = date_list[1]
                year = date_list[2]
                date_str = '{}/{}/{}'.format(year, month_dict[month], day) + ' ' + time
                article['date_publish'] = dateparser.parse(date_str)
            except:
                pass

            # fix maintext 
            try:
                maintext = ''
                for i in soup.find_all('p'):
                    maintext += i.text
                article['maintext'] = maintext.strip()
            except:
                pass

            print("newsplease date: ", article['date_publish'])
            print("newsplease title: ", article['title'])
            print("newsplease maintext: ", article['maintext'][:50])

            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'articles-{year}-{month}'
                #print(article)
            except:
                colname = 'articles-nodate'
            #print("Collection: ", colname)
            try:
                # Inserting article into the db:
                db[colname].insert_one(article)
                # count:
                url_count = url_count + 1
                print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                db['urls'].insert_one({'url': article['url']})
            except DuplicateKeyError:
                print("DUPLICATE! Not inserted.")
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")

