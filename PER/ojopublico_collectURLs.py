from bs4 import BeautifulSoup
import requests
import pandas as pd
import random
import os
import sys
import dateparser


header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


#url = 'https://ojo-publico.com/search-api?search_api_fulltext=&page=20'

base_url = 'https://ojo-publico.com/search-api?search_api_fulltext=a&page='


urls = []
for i in range(1, 250): # change here
    url = base_url + str(i)
    print('Now in:', url)
    req = requests.get(url, headers = header)

    s = BeautifulSoup(req.text,"html.parser")
    print(s)
    for i in s.find_all("div", {'class': 'card-contenido-busqueda'}):
        

        if i.find('a') is None:
            continue

        else:
            href = i.find('a')['href']
            fullurl = 'https://ojo-publico.com' + href
            print('Found:', fullurl) 
            urls.append(fullurl)
            


print('Collected', len(urls), ' links')
d = pd.DataFrame()
d['url'] = urls
d.to_csv('/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/PER/ojopublico_urls2.csv')