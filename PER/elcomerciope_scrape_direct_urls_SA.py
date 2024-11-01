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
import dateparser
import pandas as pd


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p



urls = pd.read_csv('/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/PER/elcomercio_cleanlinks_2023_05_06_07.csv')



def elcomerciope_story(soup):
    """
    Function to pull the information we want from elcomercio.pe stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}

    # Get Title: 
    try:
        article_title = soup.find("title").text
        hold_dict['title']  = article_title   
    except:
        try:
            article_titlec = soup.find("meta", {"property":"og:title"})
            article_title = article_titlec["content"] 
            hold_dict['title']  = article_title 
        except:
            hold_dict['title']  = None
        
    # Get Main Text:
    try:
        text = soup.find("p").text
        hold_dict['maintext'] = text
    except:
        hold_dict['maintext'] = None  

    # Get Date
    try:
        containsdate = soup.find("meta",{"property":"article:published_time"})
        datebit = containsdate['content']
        article_date = dateparser.parse(datebit)
        hold_dict['date_publish'] = article_date
    except:
          hold_dict['date_publish'] = None
   
    return hold_dict 




url_count = 0
processed_url_count = 0
source = 'elcomercio.pe'
for url in urls['url']:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            header = hdr = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=header)
            # process
            article = NewsPlease.from_html(response.text, url=url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            # title, maintext has no problem
            print("newsplease date: ",  article['date_publish'])
            print("newsplease title: ", article['title'])

            article['language'] = 'es'
            
            ## Fixing what needs to be fixed:
            soup = BeautifulSoup(response.content, 'html.parser')

            # TITLE
            titlec = elcomerciope_story(soup)['title']
            article['title'] = titlec
            # TEXT
            if article['maintext'] == None:
                textc = elcomerciope_story(soup)['maintext']
                article['maintext'] = textc

            if article['maintext']:
                print("newsplease maintext: ", article['maintext'][:50])

            # DATE
            datec = elcomerciope_story(soup)['date_publish']
            article['date_publish'] = datec
           
            
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
        print('\n',processed_url_count, '/', 'articles have been processed ...\n')
    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
