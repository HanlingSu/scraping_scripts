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


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
base_list = []



direct_URLs = []

# sitemap = 'https://www.sb.by/.part2.xml'
# hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
# req = requests.get(sitemap, headers = hdr)
# soup = BeautifulSoup(req.content)
# item = soup.find_all('loc')
# for i in item:
#     direct_URLs.append(i.text)

# direct_URLs = direct_URLs[-2000:]

# final_result = direct_URLs.copy()
# list(set(direct_URLs))


categorise = ['main_Incidents', 'main_world', 'main_economy', 'main_policy', 'main_society', 'tags/Окно%20в%20Китай' ]
# pages = [45, 245, 140, 60, 10, 1]

page_start = [41,183,80,60,400,7]
page_end = [40,250,110,70,550,7]
# pages = [950, 140, 80, 35, 1, 260]


for c, ps, pe in zip(categorise, page_start, page_end):
    for i in range(ps, pe+1):
        direct_URLs = []
        url = 'https://www.sb.by/articles/' + c + '/?PAGEN_2=' + str(i)
        hdr = {'User-Agent': 'Mozilla/5.0'} 
        print(url)
        time.sleep(20)
        try:
            req = requests.get(url, headers = hdr)
            soup = BeautifulSoup(req.content)
                    
            item = soup.find_all('div', {'class' : 'media-old'})
            for i in item:
                direct_URLs.append(i.find('a', href = True)['href'])
            print(len(direct_URLs))
        except:
            pass
        final_result = ['https://www.sb.by' + i for i in direct_URLs]

        print(len(final_result))

        source = 'sb.by'
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
                    #print("newsplease date: ", article['date_publish'])

                    
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Get Title: 
                    try:
                        article_title = soup.find('meta', property = 'og:title')['content']
                        article['title']  = article_title  
                    except:
                        try:
                            article_title = soup.find('title').text
                            article['title']  = article_title  
                        except:
                            try:
                                article_title = soup.find('h1').text
                                article['title']  = article_title
                            except:
                                article['title']  = article['title'] 
                    if article['title']:
                        print('newsplease title: ', article['title'])

                    # Get Main Text:
                    try:
                        maintext = soup.find('div', {'itemprop': 'articleBody'}).text
                        article['maintext'] = maintext.strip()
                    except: 
                        try:
                            maintext = soup.find('div', {'class': 'block-text'}).text
                            article['maintext'] = maintext.strip()
                        except:
                            article['maintext'] = article['maintext']
                    if article['maintext']:
                        print('newsplease main text: ', article['maintext'][:50])
                

                    # Get Date
                    try:
                        date = soup.find('meta', property="article:published_time")['content']
                        article['date_publish'] = dateparser.parse(date).replace(tzinfo=None)
                    except:
                        try:
                            date = soup.find('time').text
                            article['date_publish'] = dateparser.parse(date, settings={'DATE_ORDER': 'DMY'})
                        except:
                            article['date_publish'] = article['date_publish']
                        
                    if article['date_publish']:
                        print('newsplease date: ', article['date_publish'])

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
                print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

            else:
                pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")




