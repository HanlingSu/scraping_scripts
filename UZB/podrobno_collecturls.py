from bs4 import BeautifulSoup
import requests
import pandas as pd
import random
import os
import sys
import re
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from pymongo.errors import CursorNotFound
import pandas as pd
from datetime import date, timedelta
from newsplease import NewsPlease
from datetime import datetime
import dateparser
import time
sys.setrecursionlimit(10000)

header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# db connection
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p




# Custom Parser
def podronouz_story(soup):
    """
    Function to pull the information we want from podrobno.uz stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
       

    # Get Date
    try:
        contains_date = soup.find("time", {"class":"entry-date published updated"})
        article_date = dateparser.parse(contains_date.text)
        hold_dict['date_publish'] = article_date 
    except:
        hold_dict['date_publish'] = None
   
    return hold_dict




urls = []
source = 'podrobno.uz'

   
# r = requests.get('https://podrobno.uz/', headers = header)
# s = BeautifulSoup(r.text,"html.parser")
# print(s)


# function created
def scrape(site):
       
    # getting the request from url
    r = requests.get(site, headers = header)
       
    # converting the text
    s = BeautifulSoup(r.text,"html.parser")

    url_count = 0

    for i in s.find_all("a", href = True):
          
        href = i['href']

        ## INSERTING IN THE DB:


        if len(href.split('/')) > 4:

            if href not in urls:
                full_url = 'https://podrobno.uz' + href



                print('Scraping:', full_url)
                
                try:
                    response = requests.get(full_url, headers=header)

                except:

                    time.sleep(0.5)
                    try:
                        response = requests.get(full_url, headers=headers)
                    except:
                        continue

                try:
                    article = NewsPlease.from_html(response.text).__dict__
                    soup = BeautifulSoup(response.text, 'html.parser')

                except:
                    continue
                    
                # add on some extras
                article['date_download']=datetime.now()
                article['download_via'] = "Direct2" #change
                article['source_domain'] = source
                article['url'] = full_url 

                # insert fixes from the custom parser
                try:
                    article['maintext'] =  article['maintext'].replace('Узбекистан, Ташкент - AH Podrobno.uz.', '')
                except AttributeError:
                    pass

                article['date_publish'] = podronouz_story(soup)['date_publish']

                ## Inserting into the db
                try:
                    year = article['date_publish'].year
                    month = article['date_publish'].month
                    colname = f'articles-{year}-{month}'
                    #print(year)
                except:
                    colname = 'articles-nodate'

                try:
                    # Inserting article into the db:
                    db[colname].insert_one(article)
                    print(article['title'])
                    print(article['maintext'][0:50])
                    print(article['date_publish'])
                    
                    url_count = url_count + 1
                    print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                except DuplicateKeyError:
                    print("DUPLICATE! Not inserted.")

                urls.append(full_url)


                # calling it self
                try:
                    print('NEW URL:', full_url)
                    scrape(full_url)

                except:
                    # randomly select another href
                    print('TRY ANOTHER URL')
                    scrape(random.choice(urls))




#randomly start with some url
scrape('https://podrobno.uz/')

#url = 'https://larepublica.pe/politica/congreso/2023/04/10/congreso-fiebre-de-creacion-de-nuevas-universidades-publicas-peruanas-ministerio-de-educacion-rosendo-serna-870690'


