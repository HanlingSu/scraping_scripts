#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Jan 7 2023

@author: diegoromero

This script updates uralskweek.kz using date archives. 
"""
# Packages:
import random
import sys
sys.path.append('../')
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
import pandas as pd

# db connection:
uri = 'mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true'
db = MongoClient(uri).ml4p
#db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
#db = MongoClient('mongodb://ml4pAdmin:ml4peace@research-devlab-mongodb-01.oit.duke.edu').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

###########################################################
def uralskweekkz_story(soup):
    """
    Function to pull the information we want from uralskweek.kz stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}

    # Get Title: 
    try:
        article_title = soup.find("title").text
        hold_dict['title'] = article_title   
    except:
        hold_dict['title'] = None
        
    # Get Main Text:
    try:
        sentences = soup.findAll("p")
        #print(len(sentences))
        text = ""
        count = 0
        
        for sent in sentences:
            count = count + 1
            if count >= 6:
                if "AltynCar-қауіпсіздік" in sent:
                    text = text + ""
                else:
                    if "Enter something special:" in sent:
                        text = text + ""
                    else:
                        if 'Please enter an answer in' in sent:
                            text = text + ""
                        else: 
                            text = text + " " + sent.text                                
            else:
                pass
        text = text.replace("\n", "")
        text = text.replace("\r", "")
        text = text.replace("\t", "")
        text = text.lstrip()
        hold_dict['maintext'] = text
    except:
        hold_dict['maintext'] = None  
   
    return hold_dict 
###########################################################


## NEED TO DEFINE SOURCE!
source = 'uralskweek.kz'

years = ["2023"]
months = ["05","04"]

#years = ["2016", "2017", "2018", "2019", "2020", "2021", "2022"]
#months = ["01", "02", "03", "04", "05", "06", "07", "08", "09","10","11","12"]

list31 = ["01","03","05","07","08","10","12"]
list30 = ["02","04","06","09","11"]

for yearx in years:
    for monthx in months:
        if monthx in list30: # Pay attention here! need to chage it
            for i in range(1, 31): 
                if i <10:
                    daynum = "0" + str(i)
                else:
                    daynum = str(i)
                
                print("Month: ", monthx)
                # ENGLISH 
                url = "https://www.uralskweek.kz/" + yearx + "/" + monthx + "/" + daynum + "/"
                print("Obtaining urls for: ", url)

                urlk = "https://www.uralskweek.kz/kz/" + yearx + "/" + monthx + "/" + daynum + "/"
                
                # STEP 0: Get archive urls:
                urls = []

                reqs = requests.get(url, headers=headers)
                soup = BeautifulSoup(reqs.text, 'html.parser')
                for link in soup.find_all('a'):
                    urls.append(link.get('href')) 

                # STEP 2: keep only necessary urls:
                neededpattern = "/" + yearx + "/" + monthx + "/" + daynum + "/"

                clean_urls = []
                for url in urls:
                    if "uralskweek.kz" in url:
                        if neededpattern in url:
                            clean_urls.append(url)
                        else:
                            pass
                    else:
                        pass

                # List of unique urls:
                list_urls = list(set(clean_urls))

            
                if len(list_urls) > 0:
                    print("Total number of USABLE urls found: ", len(list_urls), ". Begin scraping.")
                    ## INSERTING IN THE DB:
                    url_count = 0
                    for url in list_urls:
                        if url == "":
                            pass
                        else:
                            if url == None:
                                pass
                            else:
                                if "uralskweek.kz" in url:
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
                                        article['language'] = 'en'
                                        
                                        ## Fixing main texts when needed:
                                        soup = BeautifulSoup(response.content, 'html.parser')

                                        # Get Main Text:
                                        article['maintext'] = uralskweekkz_story(soup)['maintext']

                                        # Get Title
                                        article['title'] = uralskweekkz_story(soup)['title']

                                        #Date:
                                        try: 
                                            urlindex = url.index(".kz/")
                                            year = url[urlindex+4:urlindex+8]
                                            month = url[urlindex+9:urlindex+11]
                                            day = url[urlindex+12:urlindex+14]
                                            article_date = datetime(int(year),int(month),int(day))
                                            article['date_publish'] = article_date
                                        except:
                                            article['date_publish'] = None

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
                                            print(article['date_publish'].month)
                                            print(article['title'][0:50])
                                            print(article['maintext'][0:100])
                                            print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                                            db['urls'].insert_one({'url': article['url']})
                                        except DuplicateKeyError:
                                            print("DUPLICATE! Not inserted.")
                                    except Exception as err: 
                                        print("ERRORRRR......", err)
                                        pass
                                else:
                                    pass

                    print("Done inserting ", url_count, " for ", neededpattern, " in English.")
                else:
                    print("Total number of USABLE urls found: ", len(list_urls), ". Next.")

                # KAZAKH (kk)
                print("Obtaining urls for: ", urlk)
                # STEP 0: Get archive urls:
                ## COLLECTING URLS
                urls = []

                reqs = requests.get(urlk, headers=headers)
                soup = BeautifulSoup(reqs.text, 'html.parser')
                for link in soup.find_all('a'):
                    urls.append(link.get('href')) 

                # STEP 2: keep only necessary urls:
                #neededpattern = "/" + str(year) + "/" + str(month) + "/" + str(daynum) + "/"

                clean_urls = []
                for url in urls:
                    if "uralskweek.kz" in url:
                        if neededpattern in url:
                            clean_urls.append(url)
                        else:
                            pass
                    else:
                        pass

                # List of unique urls:
                list_urls = list(set(clean_urls))

                if len(list_urls) > 0:
                    print("Total number of USABLE urls found: ", len(list_urls), ". Begin scraping.")
                    ## INSERTING IN THE DB:
                    url_count = 0
                    for url in list_urls:
                        if url == "":
                            pass
                        else:
                            if url == None:
                                pass
                            else:
                                if "uralskweek.kz" in url:
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
                                        article['language'] = 'kk'
                                        
                                        ## Fixing main texts when needed:
                                        soup = BeautifulSoup(response.content, 'html.parser')

                                        # Get Main Text:
                                        #article['maintext'] = uralskweekkz_story(soup)['maintext']
                                        try:
                                            sentences = soup.findAll("p")
                                            print(len(sentences))
                                            text = ""
                                            count = 0
                                            for sent in sentences:
                                                count = count + 1
                                            if count >= 6:
                                                text = text + " " + sent.text
                                            else:
                                                pass
                                            text = text.replace("\n", "")
                                            text = text.replace("\r", "")
                                            text = text.replace("\t", "")
                                            text = text.lstrip()
                                            article['maintext'] = text
                                        except:
                                            article['maintext'] = None  

                                        # Get Title
                                        article['title'] = uralskweekkz_story(soup)['title']

                                        #Date:
                                        try: 
                                            urlindex = url.index("/kz/")
                                            year = url[urlindex+4:urlindex+8]
                                            month = url[urlindex+9:urlindex+11]
                                            day = url[urlindex+12:urlindex+14]
                                            article_date = datetime(int(year),int(month),int(day))
                                            article['date_publish'] = article_date
                                        except:
                                            article['date_publish'] = None

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
                                            print(article['date_publish'].month)
                                            print(article['title'][0:50])
                                            print(article['maintext'][0:100])
                                            print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                                            db['urls'].insert_one({'url': article['url']})
                                        except DuplicateKeyError:
                                            print("DUPLICATE! Not inserted.")
                                    except Exception as err: 
                                        print("ERRORRRR......", err)
                                        pass
                                else:
                                    pass
                    print("Done inserting ", url_count, " for ", neededpattern, " in Kazakh.")
                else:
                    print("Total number of USABLE urls found: ", len(list_urls), ". Next.")

        else:
            if monthx in list31: # Pay attention here! need to chage it
                for i in range(1, 32): 
                    if i <10:
                        daynum = "0" + str(i)
                    else:
                        daynum = str(i)
                    
                    print("Month: ", monthx)
                    # ENGLISH 
                    url = "https://www.uralskweek.kz/" + yearx + "/" + monthx + "/" + daynum + "/"
                    print("Obtaining urls for: ", url)

                    urlk = "https://www.uralskweek.kz/kz/" + yearx + "/" + monthx + "/" + daynum + "/"
                    
                    # STEP 0: Get archive urls:
                    urls = []

                    reqs = requests.get(url, headers=headers)
                    soup = BeautifulSoup(reqs.text, 'html.parser')
                    for link in soup.find_all('a'):
                        urls.append(link.get('href')) 

                    # STEP 2: keep only necessary urls:
                    neededpattern = "/" + yearx + "/" + monthx + "/" + daynum + "/"

                    clean_urls = []
                    for url in urls:
                        if "uralskweek.kz" in url:
                            if neededpattern in url:
                                clean_urls.append(url)
                            else:
                                pass
                        else:
                            pass

                    # List of unique urls:
                    list_urls = list(set(clean_urls))

                
                    if len(list_urls) > 0:
                        print("Total number of USABLE urls found: ", len(list_urls), ". Begin scraping.")
                        ## INSERTING IN THE DB:
                        url_count = 0
                        for url in list_urls:
                            if url == "":
                                pass
                            else:
                                if url == None:
                                    pass
                                else:
                                    if "uralskweek.kz" in url:
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
                                            article['language'] = 'en'
                                            
                                            ## Fixing main texts when needed:
                                            soup = BeautifulSoup(response.content, 'html.parser')

                                            # Get Main Text:
                                            article['maintext'] = uralskweekkz_story(soup)['maintext']

                                            # Get Title
                                            article['title'] = uralskweekkz_story(soup)['title']

                                            #Date:
                                            try: 
                                                urlindex = url.index(".kz/")
                                                year = url[urlindex+4:urlindex+8]
                                                month = url[urlindex+9:urlindex+11]
                                                day = url[urlindex+12:urlindex+14]
                                                article_date = datetime(int(year),int(month),int(day))
                                                article['date_publish'] = article_date
                                            except:
                                                article['date_publish'] = None

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
                                                print(article['date_publish'].month)
                                                print(article['title'][0:50])
                                                print(article['maintext'][0:100])
                                                print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                                                db['urls'].insert_one({'url': article['url']})
                                            except DuplicateKeyError:
                                                print("DUPLICATE! Not inserted.")
                                        except Exception as err: 
                                            print("ERRORRRR......", err)
                                            pass
                                    else:
                                        pass

                        print("Done inserting ", url_count, " for ", neededpattern, " in English.")
                    else:
                        print("Total number of USABLE urls found: ", len(list_urls), ". Next.")

                    # KAZAKH (kk)
                    print("Obtaining urls for: ", urlk)
                    # STEP 0: Get archive urls:
                    ## COLLECTING URLS
                    urls = []

                    reqs = requests.get(urlk, headers=headers)
                    soup = BeautifulSoup(reqs.text, 'html.parser')
                    for link in soup.find_all('a'):
                        urls.append(link.get('href')) 

                    # STEP 2: keep only necessary urls:
                    #neededpattern = "/" + str(year) + "/" + str(month) + "/" + str(daynum) + "/"

                    clean_urls = []
                    for url in urls:
                        if "uralskweek.kz" in url:
                            if neededpattern in url:
                                clean_urls.append(url)
                            else:
                                pass
                        else:
                            pass

                    # List of unique urls:
                    list_urls = list(set(clean_urls))

                    if len(list_urls) > 0:
                        print("Total number of USABLE urls found: ", len(list_urls), ". Begin scraping.")
                        ## INSERTING IN THE DB:
                        url_count = 0
                        for url in list_urls:
                            if url == "":
                                pass
                            else:
                                if url == None:
                                    pass
                                else:
                                    if "uralskweek.kz" in url:
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
                                            article['language'] = 'kk'
                                            
                                            ## Fixing main texts when needed:
                                            soup = BeautifulSoup(response.content, 'html.parser')

                                            # Get Main Text:
                                            #article['maintext'] = uralskweekkz_story(soup)['maintext']
                                            try:
                                                sentences = soup.findAll("p")
                                                print(len(sentences))
                                                text = ""
                                                count = 0
                                                for sent in sentences:
                                                    count = count + 1
                                                if count >= 6:
                                                    text = text + " " + sent.text
                                                else:
                                                    pass
                                                text = text.replace("\n", "")
                                                text = text.replace("\r", "")
                                                text = text.replace("\t", "")
                                                text = text.lstrip()
                                                article['maintext'] = text
                                            except:
                                                article['maintext'] = None  

                                            # Get Title
                                            article['title'] = uralskweekkz_story(soup)['title']

                                            #Date:
                                            try: 
                                                urlindex = url.index("/kz/")
                                                year = url[urlindex+4:urlindex+8]
                                                month = url[urlindex+9:urlindex+11]
                                                day = url[urlindex+12:urlindex+14]
                                                article_date = datetime(int(year),int(month),int(day))
                                                article['date_publish'] = article_date
                                            except:
                                                article['date_publish'] = None

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
                                                print(article['date_publish'].month)
                                                print(article['title'][0:50])
                                                print(article['maintext'][0:100])
                                                print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                                                db['urls'].insert_one({'url': article['url']})
                                            except DuplicateKeyError:
                                                print("DUPLICATE! Not inserted.")
                                        except Exception as err: 
                                            print("ERRORRRR......", err)
                                            pass
                                    else:
                                        pass
                        print("Done inserting ", url_count, " for ", neededpattern, " in Kazakh.")
                    else:
                        print("Total number of USABLE urls found: ", len(list_urls), ". Next.")