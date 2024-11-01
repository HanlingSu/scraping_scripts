# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# """
# Created on Feb 3 2021

# @author: diegoromero

# This script updates 'africanews.com' using sitemaps.

# It can be run as often as one desires. 
# """
# # Packages:
# import random
# import sys
# from xml.dom import xmlbuilder
# sys.path.append('../')
# import os
# import re
# from p_tqdm import p_umap
# from tqdm import tqdm
# from pymongo import MongoClient
# import random
# from urllib.parse import urlparse
# from datetime import datetime
# from dateutil.relativedelta import relativedelta
# from pymongo.errors import DuplicateKeyError
# from pymongo.errors import CursorNotFound
# import requests
# #from peacemachine.helpers import urlFilter
# from newsplease import NewsPlease
# from dotenv import load_dotenv
# from bs4 import BeautifulSoup
# # %pip install dateparser
# import dateparser
# import pandas as pd

# # db connection:
# db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
# #db = MongoClient('mongodb://ml4pAdmin:ml4peace@research-devlab-mongodb-01.oit.duke.edu').ml4p

# ## Source:
# source = 'africanews.com'

 ## Define YEAR and MONTH to update:
year_up = 2024
month_up = 8

# ### EXTRACTING ulrs from sitemaps:
# headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# urls = []

# # Sitemaps:
# url = "https://www.africanews.com/sitemaps/en/latest-news.xml"
# print("Obtaining URLs from this sitemap: ", url)

# reqs = requests.get(url, headers=headers)
# soup = BeautifulSoup(reqs.text, 'html.parser')

# for link in soup.findAll('loc'):
#     urls.append(link.text)

# print("+ URLs so far: ", len(urls))

# url = "https://www.africanews.com/sitemaps/en/articles-2023.xml"
# print("Obtaining URLs from this sitemap: ", url)

# reqs = requests.get(url, headers=headers)
# soup = BeautifulSoup(reqs.text, 'html.parser')

# for link in soup.findAll('loc'):
#     urls.append(link.text)

# print("+ URLs so far: ", len(urls))


# url = "https://www.africanews.com/sitemaps/fr/latest-news.xml"
# print("Obtaining URLs from this sitemap: ", url)

# reqs = requests.get(url, headers=headers)
# soup = BeautifulSoup(reqs.text, 'html.parser')

# for link in soup.findAll('loc'):
#     urls.append(link.text)

# print("+ URLs so far: ", len(urls))

# # KEEP ONLY unique URLS:
# dedupurls = list(set(urls))

# # STEP 1: Get rid or urls from blacklisted sources
# blpatterns = ['/gallery/', '/tag/', '/author/', '/category/', '/tv_show/']

# list_urls = []
# for url in dedupurls:
#     if url == "":
#         pass
#     else:
#         if url == None:
#             pass
#         else:
#             try: 
#                 count_patterns = 0
#                 for pattern in blpatterns:
#                     if pattern in url:
#                         count_patterns = count_patterns + 1
#                 if count_patterns == 0:
#                     list_urls.append(url)
#             except:
#                 pass

# print("Total number of USABLE urls found: ", len(list_urls))



# ## INSERTING IN THE DB:
# url_count = 0
# for url in list_urls:
#     if url == "":
#         pass
#     else:
#         if url == None:
#             pass
#         else:
#             if 'africanews.com' in url:
#                 print(url, "FINE")
#                 ## SCRAPING USING NEWSPLEASE:
#                 try:
#                     #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
#                     header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
#                     response = requests.get(url, headers=header)
#                     # process
#                     article = NewsPlease.from_html(response.text, url=url).__dict__
#                     # add on some extras
#                     article['date_download']=datetime.now()
#                     article['download_via'] = "Direct2"
#                     article['source_domain'] = 'africanews.com'
                    
#                     ## Fixing what needs to be fixed:
#                     soup = BeautifulSoup(response.content, 'html.parser')

#                     ## FIX date:
#                     indexcom = url.index('com/')
#                     dateportion = url[indexcom+4:indexcom+14]
#                     yearp = dateportion[:4]
#                     monthp = dateportion[5:7]
#                     dayp = dateportion[8:10]
#                     article['date_publish'] = datetime(int(yearp),int(monthp),int(dayp))

#                     ## Inserting into the db
#                     # collection to update:
#                     colname_update = f'articles-{year_up}-{month_up}'

#                     try:
#                         year = article['date_publish'].year
#                         month = article['date_publish'].month
#                         colname = f'articles-{year}-{month}'
#                         #print(article)
#                     except:
#                         colname = 'articles-nodate'
#                     try:
#                         if colname == colname_update:
#                         # Inserting article into the db:
#                             db[colname].insert_one(article)
#                             # count:
#                             url_count = url_count + 1
#                             print("+TITLE: ", article['title'][0:20], " +MAIN TEXT: ", article['maintext'][0:25])
#                             print("Date extracted: ", article['date_publish'], " + Inserted! in ", colname, " - number of urls so far: ", url_count)
#                             db['urls'].insert_one({'url': article['url']})
#                         else:
#                             if colname == 'articles-nodate':
#                                 # Inserting article into the db (articles-nodate collection):
#                                 db[colname].insert_one(article)
#                                 # count:
#                                 print("+TITLE: ", article['title'][0:20], " +MAIN TEXT: ", article['maintext'][0:25])
#                                 print("No date extracted. -> Inserted in ", colname)
#                                 db['urls'].insert_one({'url': article['url']})
#                             else:
#                                 pass
#                     except DuplicateKeyError:
#                         print("DUPLICATE! Not inserted.")
#                 except Exception as err: 
#                     print("ERRORRRR......", err)
#                     pass
#             else:
#                 pass

# print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")



#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Nov 11 2021

@author: diegoromero

This script updates france24.com using daily sitemaps.
It can be run as often as one desires. 
 
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

import time

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
#db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
#db = MongoClient('mongodb://ml4pAdmin:ml4peace@research-devlab-mongodb-01.oit.duke.edu').ml4p

# headers for scraping
#headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}

#headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Safari/605.1.15 Version/13.0.4'}
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

#headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}

## NEED TO DEFINE SOURCE!
source = 'africanews.com'

list_urls = pd.read_csv('/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/INT/africanews.csv')['0']


## INSERTING IN THE DB:
url_count = 0
for url in list_urls:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if "africanews.com" in url:
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
                    
                    #try:
                    #    contains_date = soup.find("div", {"class":"post-meta-date"}).text
                        #contains_date = soup.find("i", {"class":"fa fa-calendar"}).text
                    #    article_date = dateparser.parse(contains_date, date_formats=['%d/%m/%Y'])
                    #    article['date_publish'] = article_date
                    #except:
                    #    article_date = article['date_publish']
                    #    article['date_publish'] = article_date

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
                        #print(article['date_publish'].month)
                        #print(article['title'])
                        #print(article['maintext'])
                        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        print("DUPLICATE! Not inserted.")
                        #print("Duplicated, but fixing:")
                        # Delete previous record:
                        #myquery = { "url": url}
                        #db[colname].delete_one(myquery)
                        # Adding new record:
                        #db[colname].insert_one(article)
                        #url_count = url_count + 1
                        #print("TEXT: ",article['maintext'][0:30]," + Title: ",article['title'][0:10])
                        #print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        #db['urls'].insert_one({'url': article['url']})
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
            else:
                pass


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")