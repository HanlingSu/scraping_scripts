###### Packages:

from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from pymongo import MongoClient
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import cloudscraper

import sys
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import dateparser
from pymongo.errors import DuplicateKeyError
from tqdm import tqdm
import re
import sys
import json
import time
    
import json
import pymongo
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# url = 'https://www.openzambia.com/politics'
url = 'https://www.openzambia.com/economics'
hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

direct_URLs = []
count = 0
while count <= 5:
    req = requests.get(url, headers = hdr)
    soup = BeautifulSoup(req.content)
    
    for article in soup.find_all('article'):
        direct_URLs.append(article.find('a')['href'])
    print(len(direct_URLs))
    nav = soup.find('nav', {'class' : 'BlogList-pagination'}).find_all('a')
    if 'offset' in url and len(nav) ==1:
        break
    url = 'https://www.openzambia.com' + nav[-1]['href']
    print(url)
    count += 1
    time.sleep(0.5)


pd.DataFrame(direct_URLs).to_csv('/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/ZMB/openzambia.csv')