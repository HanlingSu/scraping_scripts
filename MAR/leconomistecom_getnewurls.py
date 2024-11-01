# Packages:
from pymongo import MongoClient
from bs4 import BeautifulSoup
from newspaper import Article
from dateparser.search import search_dates
import dateparser
import requests
from pymongo import MongoClient
from urllib.parse import urlparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from pymongo.errors import CursorNotFound
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from dotenv import load_dotenv
import re


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []
source = 'leconomiste.com'



base = 'https://www.leconomiste.com/sitemap.xml?page='


for i in range(257, 258):
    base_link = base + str(i) 
    print(base_link)
     #header settings
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = requests.get(base_link, headers = hdr)
    soup = BeautifulSoup(req.content)
    item = soup.find_all('loc')

    for i in item:
        direct_URLs.append(i.text)

    print('Now scraped ', len(direct_URLs), ' articles from previous pages.')

blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

final_result = direct_URLs.copy()

# https://www.leconomiste.com/categorie/Economie?page=5
    # direct_URLs = []
    # categories = ['economie', 'International', 'Régions', 'Finances-Banques', 'Enterprises', 'Société', 'Politique']
    # page_start = [1, 1, 1, 1, 1, 1, 1]
    # page_end = [20, 9, 6, 2, 6, 6, 3]
    # base = 'https://www.leconomiste.com/categorie/'

    # for c, ps, pe in zip(categories, page_start, page_end):
    #     for p in range(ps, pe+1):
    #         base_link = base + c + '?page=' + str(p) 
    #         print(base_link)
    #         hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
    #         req = requests.get(base_link, headers = hdr)
    #         soup = BeautifulSoup(req.content)
    #         item = soup.find_all('div', {'class' : 'col-xs-12 col-sm-12 col-md-6 col-lg-6'})

    #         for i in item:
    #             direct_URLs.append(i.find('a')['href'])

    #         print('Now scraped ', len(direct_URLs), ' articles from previous pages.')
        


# full_urls = []
# for url in direct_URLs:
#     full_url = 'https://www.leconomiste.com/' + url
#     full_urls.append(full_url)


    
# final_result = list(set(full_urls))




print('Total number of urls found: ', len(final_result))

url_count = 0
processed_url_count = 0
for url in final_result[::-1]:
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
            # fix date and maintext
            print("newsplease title: ", article['title'])
           


            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # get category
            try:
                category = soup.find('div', {'class' : 'TitleBlog'}).text.strip()
            except:
                category = 'News'

            if category not in ['De bonnes sources', 'Analyse', 'Entreprises', 'Compétences & Innovation', 'Culture',\
                                'Courrier des Lecteurs', "L'Édito"]:
                
                stringtest = "L'article auquel vous tentez d'accéder est réservé à la communauté des grands lecteurs de L'Economiste"
        
                # fix maintext
                if not article['maintext'] and stringtest in article['maintext']:
                    try:
                        soup.find('div', {'class' : 'point'}).find_all('div', {'class' : re.compile('field-item .*')})
                        maintext = ''
                        for i in soup.find('div', {'class' : 'point'}).find_all('div', {'class' : re.compile('field-item .*')}):
                            maintext += i.text
                        article['maintext'] = maintext 
                    except: 
                        try:
                            soup.find('div', {'class' : 'body'}).find_all('p')
                            maintext = ''
                            for i in soup.find('div', {'class' : 'body'}).find_all('p'):
                                maintext += i.text
                            article['maintext'] = maintext 
                        except:
                            try:
                                contains_maintext = soup.find("meta", {"name": "description"})
                                maintext = contains_maintext['content']
                                article['maintext'] = maintext 
                            except:
                                try:
                                    maintext = soup.find('p', {'class': 'rtejustify'}).text

                                    if stringtest in maintext:
                                        maintext = None
                                        article['maintext'] = None
                                    else:
                                        article['maintext'] = maintext

                                except:
                                    article['maintext'] =None
                if article['maintext']:
                    print('Manual scpraed maintext', article['maintext'][:50])

                # fix Date
                try:
                    date = soup.find('div', {'class' : 'author'}).text.split('Economiste', 1)[1].split('Le ', 1)[1].split('|')[0]
                    article['date_publish'] = dateparser.parse(date, settings={'DATE_ORDER': 'DMY'})

                except:
                    try:
                        contains_date = soup.find("meta", {"property": "article:published_time"})
                        article_date = dateparser.parse(contains_date['content']).replace(tzinfo= None)
                        article['date_publish'] = article_date  
                        print('2')
                    except:
                        article_date = None
                        article['date_publish'] = None  
                        
                if article['date_publish']:
                    print('Manual scpraed date_publish', article['date_publish'])
            
            else:
                article['title'] = 'From uninterested categories: ' + category
                article['date_publish'] = None
                article['maintext'] = None
                print(article['title'])

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
