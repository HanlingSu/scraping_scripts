import random
import sys
import os
import re
from p_tqdm import p_umap
from tqdm import tqdm
from pymongo import MongoClient
import random
from urllib.parse import urlparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from pymongo.errors import CursorNotFound
import requests
#from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from dotenv import load_dotenv
import cloudscraper
from bs4 import BeautifulSoup, SoupStrainer
import dateparser

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)


def download_url(uri, url, download_via=None, insert=True, overwrite=False):
    """
    process and insert a single url
    """
    db = MongoClient(uri).ml4p

    try:
        # download
        #print('First Try ', url)
        #header = {
        #    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        #}
        #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
        header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        response = requests.get(url, headers=header)
        
        # process
        article = NewsPlease.from_html(response.text, url=url).__dict__
        # add on some extras
        article['date_download']=datetime.now()
        if download_via:
            article['download_via'] = download_via
        # insert into the db
        if not insert:
            print("Not Inserted ", url)
            return article
        
        ### Custom scraping
        soup = BeautifulSoup(scraper.get(url).text, 'html.parser')
        try:
            title = soup.find('div', {'class' : 'content-title'}).find('h1').text
            article['title'] = title
        except:
            title = soup.finf('meta', property = 'og:title')['content']
            article['title'] = title
        print("newsplease title: ", article['title'])
        
        
        try:
            date = soup.find('meta', property = 'article:published_time')['content']
            print(date)
            if 'CEST' in date:
                date = date.replace('CEST', ' ')
            elif 'CET' in date:
                date = date.replace('CET', ' ')
            article['date_publish'] = dateparser.parse(date)
        except:
            date = soup.find('span', {'class' : 'a-time'}).text
            article['date_publish'] = dateparser.parse(date)
        print("newsplease date: ", article['date_publish'])
        
        try:
            maintext = ''
            for i in soup.find('div', {'class' : 'content-narrow'}).find_all('p'):
                maintext += i.text
            article['maintext'] = maintext.strip()
        except:
            maintext = soup.find('div', {'class' : 'content-narrow'}).text
            article['maintext'] = maintext.strip()
        print("newsplease maintext: ", article['maintext'][:100])
            
            
     
        if article:
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'articles-{year}-{month}'
            except:
                colname = 'articles-nodate'
            try:
                if overwrite:
                    db[colname].replace_one(
                        {'url': url},
                        article,
                        upsert=True
                    )
                else:
                    db[colname].insert_one(
                        article
                    )
                    print("Inserted! in ", colname)
                    db['direct-urls'].delete_one({
                        'url' : url
                    })
                db['urls'].insert_one({'url': article['url']})
                
            except DuplicateKeyError:
                print("DUPLICATE! deleting")
                db['direct-urls'].delete_one({
                    'url' : url
                })
        return article
    except Exception as err: 
        print("ERRORRRR......", err)
        pass


def main():
    load_dotenv()
    #uri = 'mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p'
    uri = 'mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true'

    #uri = os.getenv('DATABASE_URL')
    db = MongoClient(uri).ml4p
    batch_size = 128
    
    colname = 'direct-urls'
    source_domains = db.sources.distinct('source_domain', filter={'include' : True, 'primary_location' : 'ALB'})
    #source_domains = db.sources.distinct('source_domain', filter={'include' : True, 'major_regional': True})
    #source_domains = db.sources.distinct('source_domain', filter={'include' : True, 'major_international': True})
    sources_re = "|".join(source_domains)

    try:
        cursor = db[colname].find({
            # specific source domain 
            #'url': {'$regex': 'univision.com'}
            'url': {'$regex': 'gazetatema.net'}
            #'url' : {'$regex' : 'portafolio.co'}
        }) 

        list_urls = []
        
        for _doc in tqdm(cursor):
            # print(_doc['url']) #make sure the urls are correct
            # modify direct URLs if needed
            if 'feed/' in _doc['url']:
                _doc['url'] = _doc['url'][:-5]
            if '\ufeff' in _doc['url']:
                _doc['url'] = _doc['url'].replace("\ufeff", "")
            if "https:/w" in _doc['url']:
                #print('yes')
                _doc['url'] = _doc['url'].replace("https:/w", "https://w")   
            list_urls.append(_doc['url'])
            print(_doc['url']) 
            
            if len(list_urls) >= batch_size:
                print('Extracting urls')
                try:
                    p_umap(download_url, [uri]*len(list_urls), list_urls, ['direct']*len(list_urls), num_cpus=10)
                except ValueError:
                    print('ValueError')
                except AttributeError:
                    print('AttributeError')
                except Exception as err:
                    print('Here:', err)
                list_urls = []
        p_umap(download_url, [uri]*len(list_urls), list_urls, ['direct']*len(list_urls), num_cpus=10)
        list_urls = []
    except CursorNotFound:
        print('cursor not found')
        pass

if __name__== '__main__':
    main()