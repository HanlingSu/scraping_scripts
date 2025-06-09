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


categories = ['nasional','metro', 'daerah', 'ekbis', 'international']  
categories_num = [5, 6, 7, 8, 9]
# page_start = [0,0,0,0,0]
# page_end = [6300,3400, 5300, 4800, 3700]
# page_end = [5500,3500, 5300, 4200, 2800]
# page_end = [9018, 5100, 7425, 6426, 4000]

# link = 'https://video.sindonews.com/vod/' # {'class' : 'video-title'} 'https://international.sindonews.com/more/9/', 
   
# for c, cn, ps, pe in zip(categories, categories_num, page_start, page_end):
#     direct_URLs = []     

#     for p in range(ps, pe, 20):
#         # print(p)
#         url ='https://'+ c + '.sindonews.com/more/' + str(cn) +'/' +str(p) 
#         print(url)
#         hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
#         req = requests.get(url, headers = hdr)
#         soup = BeautifulSoup(req.content)

#         item =  soup.find_all('div', {'class' : 'content-kanal-topik pt0 pl16 sm-width-auto'})
#         for i in item:
#             direct_URLs.append(i.find('a')['href'])

#         print('Now scraped ', len(direct_URLs), ' articles from previous pages.')
source = 'sindonews.com'




for year in range(2025, 2026):
    year_str = str(year)
    for month in range(1, 4):
        direct_URLs = []
        if month <10:
            month_str = '0'+str(month)
        else:
            month_str = str(month)
        for day in range(1, 32):
            if day <10:
                day_str = '0'+str(day)
            else:
                day_str = str(day)
            for cn in categories_num:
                for p in range(0, 200, 20):
                    
                    link = 'https://index.sindonews.com/index/' + str(cn) +'/' + str(p) + '?t=' +year_str+'-'+month_str+'-'+day_str
                
                    hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
                    req = requests.get(link, headers = hdr)
                    soup = BeautifulSoup(req.content)
                    item = soup.find_all('div', {'class' : 'indeks-title'})
                    for i in item:
                        direct_URLs.append(i.find('a')['href'])
            print(link)
            print('Now scraped ', len(direct_URLs), ' articles from previous pages.')


        blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
        blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
        direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

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
                    print("newsplease date: ", article['date_publish'])
                    print("newsplease title: ", article['title'])
        #             print("newsplease maintext: ", article['maintext'])
                    
                    
                    # custom parser
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    try:
                        maintext = soup.find('div', {'class' : 'detail-desc'}).text.strip()
                        article['maintext'] = maintext
                    except:
                        try:
                            maintext = soup.find('div', {'id' : 'content'}).text.strip()
                            article['maintext'] = maintext
                        except:
                            maintext = None
                            article['maintext'] = maintext
                    print("newsplease maintext: ", article['maintext'][:50])
                    
        #             
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
                        print("DUPLICATE! Not inserted.")
                        pass
                        
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
            else:
                pass
            processed_url_count += 1
                            
            print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')
                            
        print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
