#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 23, 2022

@author: diegoromero

This script updates lesoleil.sn using queries per section. 
This script can be ran whenever needed (just make the necessary modifications).
 
"""
# Packages:
import time
import sys
sys.path.append('../')
from pymongo import MongoClient
from urllib.parse import urlparse
from datetime import datetime
from pymongo.errors import DuplicateKeyError
import requests
from newsplease import NewsPlease
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import dateparser

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

def lesoleilsn_story(soup):
    """
    Function to pull the information we want from lesoleil.sn stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
    # Get Title: 
    try: 
        article_title = soup.find("title").text
        hold_dict['title']  = article_title   
    except:
        try:
          contains_title = soup.find("meta", {"property":"og:title"})
          article_title = contains_title['content']
          hold_dict['title']  = article_title 
        except: 
          article_title = None
          hold_dict['title'] = None
        
    # Get Main Text:
    try:
        sentences = soup.findAll("p", {"style":"text-align: justify;"})
        if len(sentences) > 3:
          maintext = sentences[0].text + " " + sentences[1].text + " " + sentences[2].text 
        else:
          if len(sentences) == 2:
            maintext = sentences[0].text + " " + sentences[1].text
          else:
            maintext = sentences[0].text
        hold_dict['maintext'] = maintext
    except: 
        try:
            sentences = soup.findAll("p")
            if len(sentences) > 2:
              maintext = sentences[1].text + " " + sentences[2].text 
            else:
              if len(sentences) == 2:
                maintext = sentences[1].text
              else:
                maintext = sentences[0].text
            hold_dict['maintext'] = maintext
        except: 
            maintext = None
            hold_dict['maintext'] = None

    # Get Date
    try: 
        months = ['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre']
        contains_date = soup.find("span", {"class":"tt-post-date-single"}).text
        contains_datelist = contains_date.split()
        dayn = int(contains_datelist[0])
        yearn = int(contains_datelist[2])
        monthn = months.index(contains_datelist[1]) + 1
        article_date = datetime(int(yearn),int(monthn),int(dayn))
        #article_date = dateparser.parse(article_date, date_formats=['%d/%m/%Y'])
        hold_dict['date_publish'] = article_date  

    except:
        article_date = None
        hold_dict['date_publish'] = None  
   
    return hold_dict 

## NEED TO DEFINE SOURCE!
source = 'lesoleil.sn'

# STEP 1: Extracting urls from key sections:
#sections = ['category/actualites/politique/','category/actualites/international/']
#number = ['2','3']
#sections = ['category/actualites/politique/','economie/','la-regionale/']
#number = ['927','900','1000']
#number = ['927','2072','2072']

sections = ['category/actualites/politique/','category/actualites/international/','category/actualites/sante/','category/actualites/environnement/',\
            'economie/','category/actualites/education/','category/actualites/societe/','category/actualites/regions/','la-regionale/']
numberinit = ['1','1','1','1','1','1','1','1','1']
#numberinit = ['71','16','50','29','125','30','82','53','125']
number = ['2','2','2','2','2','2','2','2','2']
#number = ['927','172','198','59','2072','76','495','120','2072']

for sect in sections:
    time.sleep(2)
    ## COLLECTING URLS
    urls = []
    indexsect = sections.index(sect)
    numberix = numberinit[indexsect]
    numberx = number[indexsect]
    for i in range(int(numberix),int(numberx)+1):
        if i == 1:
            url = "http://lesoleil.sn/" + sect
        else:
            url = "http://lesoleil.sn/" + sect + "page/" + str(i) + "/"

        print("Extracting from ", url)

        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        for link in soup.find_all('a', {'class' : 'tt-post-title c-h5'}):
            urls.append(link.get('href')) 

        print("+ Number of urls so far: ", len(urls))

    # Manually check urls:
    #dftest = pd.DataFrame(list_urls)  
    #dftest.to_csv('/Users/diegoromero/Downloads/test.csv')  

    # STEP 2: Get rid or urls from blacklisted sources
    blpatterns = ['/wp-json/', '/photo/', ':80/', '/art/', '/index.php/', '/wp-content/', '/images/','/category/','/page/']

    # List of unique urls:
    dedup = list(set(urls))
    list_urls = []

    for url in dedup:
        if url == None:
            pass
        else:
            if url == "":
                pass
            else:
                if "lesoleil.sn" in url:
                    count_patterns = 0
                    for pattern in blpatterns:
                        if pattern in url:
                            count_patterns = count_patterns + 1
                    if count_patterns == 0:
                        list_urls.append(url)


    print("Total number of USABLE urls found: ", len(list_urls))


    ## INSERTING IN THE DB:
    url_count = 0
    processed_url_count = 0
    for url in list_urls:
        if url == "":
            pass
        else:
            if url == None:
                pass
            else:
                if "lesoleil.sn" in url:
                    print(url, "FINE")
                    time.sleep(1)
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
                        article['source_domain'] = 'lesoleil.sn'
                        article['language'] = 'fr'

                        
                        ## Fixing Date, Main Text and Title:
                        response = requests.get(url, headers=header).text
                        soup = BeautifulSoup(response)

                        ## Title
                        article['title'] = lesoleilsn_story(soup)['title'] 
                        ## Main Text
                        article['maintext'] = lesoleilsn_story(soup)['maintext'] 
                        ## Date
                        article['date_publish'] = lesoleilsn_story(soup)['date_publish'] 

                        ## Inserting into the db
                        try:
                            year = article['date_publish'].year
                            month = article['date_publish'].month
                            colname = f'articles-{year}-{month}'
                            #print(article)
                        except:
                            colname = 'articles-nodate'
                        try:
                            #TEMP: deleting the stuff i included with the wrong domain:
                            #myquery = { "url": final_url, "source_domain" : 'web.archive.org'}
                            #db[colname].delete_one(myquery)
                            # Inserting article into the db:
                            db[colname].insert_one(article)
                            # count:
                            url_count = url_count + 1
                            #print(article['date_publish'])
                            print("Title: ", article['title'][0:25]," + Main Text: ", article['maintext'][0:30])
                            print(article['maintext'][:50])
                            print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                            db['urls'].insert_one({'url': article['url']})
                        except DuplicateKeyError:
                            print("DUPLICATE! Not inserted.")
                    except Exception as err: 
                        print("ERRORRRR......", err)
                        pass
                                
                    processed_url_count += 1
                    print('\n',processed_url_count, '/', len(list_urls), 'articles have been processed ...\n')

                else:
                    pass


    print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")