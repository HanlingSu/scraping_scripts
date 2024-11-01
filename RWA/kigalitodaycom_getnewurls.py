"""
Created on Oct 26, 2022 

Craated by Hanling Su
"""

# Packages:

from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from datetime import datetime
from pymongo.errors import DuplicateKeyError
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
import re

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p



base = 'https://www.kigalitoday.com/'
source = 'kigalitoday.com'

category = ['amakuru/amakuru-mu-rwanda', 'amakuru/muri-afurika', 'amakuru/mu-mahanga', 'amakuru/utuntu-n-utundi', \
           'amakuru/amatora', 'ubutabera', 'kwibuka', 'ubukungu/iterambere', 'ubukungu/ubwiteganyirize', 'ubukungu/ubucuruzi', \
           'ubukungu/ivunjisha', 'umutekano']
page_start = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
page_end = [500, 29, 120, 29, 30, 60, 0, 29, 29, 29, 29, 60]

for ps, pe, c in zip(page_start, page_end, category):
    direct_URLs = []
    for p in range(ps, pe+1, 30):
        link = base + c + '/?debut_amakuruaheruka_fromrub_arts1=' + str(p) +'#pagination_amakuruaheruka_fromrub_arts1'
#         print(link)
        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
        req = requests.get(link, headers = hdr)
        soup = BeautifulSoup(req.content)
        for h3 in soup.find_all('h3', {'class' : 'headline'}):
            direct_URLs.append(h3.find('a')['href'])
        print(len(direct_URLs))

    blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
    blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
    direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

    final_result = direct_URLs.copy()

    final_result = ['https://www.kigalitoday.com/' + i for i in direct_URLs]
    print('Now have collected', len(final_result), 'articles from', c)


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
                article['language'] = 'rw'

                
                soup = BeautifulSoup(response.content, 'html.parser')

                # fix date
                try:
                    date = soup.find('time', {'class':"timestamp"}).text.strip()[:18]
                    article['date_publish'] = dateparser.parse(date, settings={'DATE_ORDER': 'DMY'})
                except:
                    date = soup.find('time', {'class':"timestamp"}).text.split('\'\xa0')[0].strip()
                    article['date_publish'] = dateparser.parse(date, settings={'DATE_ORDER': 'DMY'})
                
                # fix maintext
                try:
                    maintext = ''
                    for i in soup.find('div', {'itemprop' : 'articleBody'}).find_all('p'):
                        maintext += i.text
                    article['maintext'] = maintext.strip()
                except:
                    try:
                        maintext = ''
                        for i in soup.find_all('p'):
                            maintext += i.text
                        article['maintext'] = maintext.strip()
                        article['maintext'] = article['maintext'] 
                    except:
                        maintext = soup.find('h2', {'itemprop' : 'description'}).text
                        article['maintext'] = article['maintext'] 

                print("newsplease date: ", article['date_publish'])
                print("newsplease title: ", article['title'])
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
                    # db[colname].delete_one({ "url": url, "source_domain" : source})
                    # db[colname].insert_one(article)
                    
                    print("DUPLICATE! Pass.")
                    
            except Exception as err: 
                print("ERRORRRR......", err)
                pass
            processed_url_count += 1
            print('\nNow scraping ', c)
            print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

        else:
            pass

    print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
