
# Packages:
from typing import final
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import dateparser
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import re

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'vb.kg'


url_count = 0
processed_url_count = 0
len_final_result = 0
base = 'https://www.vb.kg/?date='

for year in range( 2024, 2025):
    year_str = str(year)
    for month in range(5, 6):
        direct_URLs = []
        if month<10:
            month_str = '0' + str(month)
        else:
            month_str = str(month)
        for day in range(1, 32):
            if day<10:
                day_str = '0' + str(day)
            else:
                day_str = str(day)
            for category in ['1',     '2',     '3',      '5']:
                        # policy, economic, society, incident

                url = base + year_str + '-' + month_str +'-' +day_str + '&lable=' + category +'&order=time#paginator'
                print(url)
                hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'} #header settings
                try:
                    req = requests.get(url, headers = hdr)
                    soup = BeautifulSoup(req.content)
                    items = soup.find_all('div', {'class' : 't f_medium'})
                    for i in items:
                        direct_URLs.append(i.find('a')['href'])
                except:
                    pass
            print('Now collected ', len(direct_URLs), 'articles from previous pages...')


        final_result = direct_URLs.copy()
        len_final_result += len(final_result)
        print(len(final_result))

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
        
                    ## Fixing Date:
                    soup = BeautifulSoup(response.content, 'html.parser')

                   
                    print("newsplease title: ", article['title'])
                    # main text:
                    try:
                        maintext = soup.find('div', {'class' : 'topic-text'}).text
                        article['maintext'] = maintext.strip()
                    except:
                        maintext = ''
                        soup.find('div', {'class' : 'topic-text'}).find_all('p')
                        for i in soup.find('div', {'class' : 'topic-text'}).find_all('p'):
                            maintext += i.text
                        article['maintext'] = maintext.strip()
                    print("newsplease maintext: ", article['maintext'][:50])

                    # date
                    try:
                        date = soup.find('time')['datetime']
                        article['date_publish'] = dateparser.parse(date).replace(tzinfo = None)
                    except:
                        date = soup.find('div', {'class' :'topic_time_create'}).text
                        article['date_publish'] = dateparser.parse(date)
                    print("newsplease date: ", article['date_publish'])
                    

                    try:
                        year = article['date_publish'].year
                        month = article['date_publish'].month
                        colname = f'articles-{year}-{month}'
                        #print(article)
                    except:
                        colname = 'articles-nodate'
                    #print("Collection: ", colname)
                    try:
                        #TEMP: deleting the stuff i included with the wrong domain:
                        #myquery = { "url": final_url, "source_domain" : 'web.archive.org'}
                        #db[colname].delete_one(myquery)
                        # Inserting article into the db:
                        db[colname].insert_one(article)
                        # count:
                        if colname != 'articles-nodate':
                            url_count = url_count + 1
                            print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        print("DUPLICATE! Not inserted.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
                processed_url_count += 1
                print('\n',processed_url_count, '/', len_final_result, 'articles have been processed ...\n')

            else:
                pass

        print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
