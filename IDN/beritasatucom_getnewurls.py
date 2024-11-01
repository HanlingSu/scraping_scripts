
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

url_count = 0
processed_url_count = 0

source = 'beritasatu.com'
direct_URLs = []
j = 0
page_start =  1048000
page_end = 1066559
# 1034936
total_article = page_end - page_start
for i in range(page_start, page_end):
    j += 1
    # 1007001,1014001, 1010001
    url = 'https://www.beritasatu.com/news/' + str(i) +'/'

    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    response = requests.get(url, headers=header)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    try:
        link = soup.find('meta', property = 'og:url')['content']
        print(link)
        direct_URLs.append(link)

    except:
        pass
    print(len(direct_URLs))
    
    if j % 10 == 0:

        blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
        blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
        final_result = [word for word in direct_URLs if not blacklist.search(word)]


        print(len(final_result))
        total_article = total_article-len(direct_URLs)+len(final_result)
        for url in final_result:
            if url:
                
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
                    print("newsplease title: ", article['title'])
                    
                
                    soup = BeautifulSoup(response.content, 'html.parser')
                    url = soup.find('meta', property = 'og:url')['content']
                    article['url'] = url
                    print(url, "FINE")
                    # fix date
                    try:
                        date = soup.find_all('script', type="application/ld+json")[1].string.split('"datePublished":', 1)[1].split(',', 1)[0]
                        date_publish = dateparser.parse(date).replace(tzinfo = None) 
                        article['date_publish'] = date_publish

                    except:
                        try:
                            date = soup.find('p', {'class' : 'editor'}).text.split('WIB')[0]
                            if ',' in date:
                                date = date.split(',',1)[1]
                            else:
                                date = date
                            date_publish = dateparser.parse(date).replace(tzinfo = None) 
                            article['date_publish'] = date_publish
                        except:
                            try:
                                date = soup.find('div', {'class' : 'small'}).text.split(',', 1)[1].split('WIB')[0]
                                if ',' in date:
                                    date = date.split(',',1)[1]
                                else:
                                    date = date
                                date_publish = dateparser.parse(date).replace(tzinfo = None) 
                                article['date_publish'] = date_publish
                            except:
                                article['date_publish'] = None
                    print("newsplease date: ", article['date_publish'])
                    
                    # fix main text
                    try:
                        if len(soup.find_all('div', {'class': 'story'})) > 1:
                            maintext = soup.find_all('div', {'class': 'story'})[1].text
                            article['maintext'] = maintext.strip().replace('Beritasatu.com -', '')
                        

                    except:
                        try:
                            maintext = soup.find('div', {'class':"story"}).text
                            article['maintext'] = maintext.strip().replace('Beritasatu.com -', '')

                        except:
                            article['maintext'] = article['maintext'].replace('Beritasatu.com –', '')
                    if article['maintext']:
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
                        #TEMP: deleting the stuff i included with the wrong domain:
                        #myquery = { "url": final_url, "source_domain" : 'web.archive.org'}
                        #db[colname].delete_one(myquery)
                        # Inserting article into the db:
                        db[colname].insert_one(article)
                        # count:
                        if colname != 'articles-nodate':
                            url_count = url_count + 1
                            print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        else:
                            print("Inserted! in ", colname)
                        db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        print("DUPLICATE! Not inserted.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
                processed_url_count += 1
                
                print('\n',processed_url_count, '/', str(total_article), 'articles have been processed ...\n')

            else:
                pass
        direct_URLs = []
        print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")

