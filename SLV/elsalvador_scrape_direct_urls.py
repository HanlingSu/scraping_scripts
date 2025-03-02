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

from bs4 import BeautifulSoup
# %pip install dateparser
import dateparser


def elsalvadorcom_story(soup):
        """
        Function to pull the information we want from elsalvador.com stories
        :param soup: BeautifulSoup object, ready to parse
        """
        hold_dict = {}
        
        # Get Title: 
        try:
            contains_title = soup.find("meta", {"property":"og:title"})
            article_title = contains_title['content']
            hold_dict['title']  = article_title   
        except:
            try:
                article_title = soup.find("title").text
                hold_dict['title']  = article_title   
            except:
                hold_dict['title']  = None
            
        # Get Main Text:
        try:
            contains_maintext = soup.find("meta", {"property":"og:description"})
            article_maintext = contains_maintext['content']
            hold_dict['maintext'] = article_maintext
        except: 
            try: 
                maintext_contains = soup.findAll("p")
                maintext = maintext_contains[2].text + " " + maintext_contains[3].text + " " + maintext_contains[4].text
                hold_dict['maintext'] = maintext
            except:
                hold_dict['maintext']  = None

        # Get Date (not for /amp/)
        try:
            datex = soup.find("span", {"class":"datetime"}).text
            datex = datex.replace(".", " ")
            #print(datex)
            datevector = datex.split()
            dayx = datevector[0]
            monthx = datevector[1]
            monthx = monthx.lower()
            yearx = datevector[2]
            #print(dayx, monthx, yearx)
            month3 = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
            indexm = month3.index(monthx)
            article_date = datetime(int(yearx),int(indexm+1),int(dayx))
            #print(article_date)
            hold_dict['date_publish'] = article_date 
        except:  
            try:
                datex = soup.find("span", {"class":"article-datetime"}).text
                datex = datex.replace(".", " ")
                #print(datex)
                datevector = datex.split()
                dayx = datevector[0]
                monthx = datevector[1]
                monthx = monthx.lower()
                yearx = datevector[2]
                #print(dayx, monthx, yearx)
                month3 = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
                indexm = month3.index(monthx)
                article_date = datetime(int(yearx),int(indexm+1),int(dayx))
                #print(article_date)
                hold_dict['date_publish'] = article_date 
            except:  
                try:  
                    contains_date = soup.find("meta", {"property":"article:published_time"})
                    article_date = contains_date['content']
                    #article_date = dateparser.parse(article_date,date_formats=['%d/%m/%Y'])
                    article_date = dateparser.parse(article_date)
                    hold_dict['date_publish'] = article_date  
                except:
                    try:
                        contains_date = soup.find("meta", {"name":"date"}) 
                        article_date = contains_date['content']
                        article_date = dateparser.parse(article_date,date_formats=['%d/%m/%Y'])
                        hold_dict['date_publish'] = article_date 
                    except:
                        try:
                            contains_date = soup.find("meta", {"name":"moddate"})
                            article_date = contains_date['content']
                            article_date = dateparser.parse(article_date)
                            hold_dict['date_publish'] = article_date 
                            #name="moddate" content="2017-01-02T18:47:45-06:00"
                        except:
                            try:
                                datex = soup.find("span", {"class":"ago"}).text
                                datex = datex.replace(",", "")
                                datex = datex.replace("-", "")
                                datex = datex.replace(".", "")
                                #print(datex)
                                datevector = datex.split()
                                dayx = datevector[1]
                                monthx = datevector[0]
                                monthx = monthx.lower()
                                yearx = datevector[2]
                                #print(dayx, monthx, yearx)
                                month3 = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
                                indexm = month3.index(monthx)
                                article_date = datetime(int(yearx),int(indexm+1),int(dayx))
                                #print(article_date)
                                hold_dict['date_publish'] = article_date 
                            except:  
                                try: 
                                    datex = soup.find("span", {"class":"ago"}).text
                                    datex = datex.replace(",", "")
                                    datex = datex.replace("-", "")
                                    datex = datex.replace(".", "")
                                    dayx = datex[0:2]
                                    monthx = datex[2:5]
                                    monthx = monthx.lower()
                                    yearx = datex[5:9]
                                    month3 = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
                                    indexm = month3.index(monthx)
                                    article_date = datetime(int(yearx),int(indexm+1),int(dayx))
                                    hold_dict['date_publish'] = article_date 
                                except:
                                    hold_dict['date_publish'] = None
    
        return hold_dict 

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
        ## Fixing what needs to be fixed:
        soup = BeautifulSoup(response.content, 'html.parser')
        article['date_publish'] = elsalvadorcom_story(soup)['date_publish']
        article['date_download'] = datetime.now()
        if download_via:
            article['download_via'] = download_via
        # insert into the db
        if not insert:
            print("Not Inserted ", url)
            return article
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
                    print(" ++ ", article['date_publish'], "Inserted! in ", colname)
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
    source_domains = db.sources.distinct('source_domain', filter={'include' : True, 'primary_location' : 'SLV'})
    #source_domains = db.sources.distinct('source_domain', filter={'include' : True, 'major_regional': True})
    #source_domains = db.sources.distinct('source_domain', filter={'include' : True, 'major_international': True})
    sources_re = "|".join(source_domains)

    try:
        cursor = db[colname].find({
            # specific source domain 
            #'url': {'$regex': 'univision.com'}
            'url': {'$regex': 'elsalvador.com'}
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