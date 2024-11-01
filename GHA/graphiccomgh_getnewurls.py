#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Nov 1 2021

@author: diegoromero

This script updates graphic.com.gh -- it must be edited to 
scrape the most recent articles published by the source.

It needs to be run everytime we need to update GHA sources. 
"""
# Packages:
from pymongo import MongoClient
from bs4 import BeautifulSoup
from dateparser.search import search_dates
import dateparser
import requests
from urllib.parse import quote_plus
import time
from datetime import datetime
from pymongo.errors import DuplicateKeyError
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from dotenv import load_dotenv


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


## COLLECTING URLS
urls = []

## NEED TO DEFINE SOURCE!
source = 'graphic.com.gh'

## STEP 0: URLS FROM SITEMAP:
# url_sitemaps = ["https://www.graphic.com.gh/component/jmap/sitemap/xml?format=xml", "https://www.graphic.com.gh/index.php?option=com_jmap&view=sitemap&format=xml", "https://www.graphic.com.gh/component/jmap/sitemap/gnews?format=gnews", "https://www.graphic.com.gh/index.php?option=com_jmap&view=sitemap&format=amp", "https://www.graphic.com.gh/index.php?option=com_jmap&view=sitemap&format=mobile"]
# #url_sitemaps = ["https://www.graphic.com.gh/sitemap_amp_0.xml", "https://www.graphic.com.gh/sitemapfiles/sitemap_xml_0.xml","https://www.graphic.com.gh/sitemapfiles/sitemap_xml_1.xml","https://www.graphic.com.gh/sitemapfiles/sitemap_xml_2.xml",]
# for url in url_sitemaps:
#     print("Sitemap: ", url)
#     reqs = requests.get(url, headers=headers)
#     soup = BeautifulSoup(reqs.text, 'html.parser')
#     for link in soup.findAll('loc'):
#         urls.append(link.text)
#     print(len(urls))

## STEP 1: URLS FROM TOPICS

## TOPICS 
#keywords = ['elections']
#endnumber = ['3']

keywords = ['elections','judge','national%20assembly','president','protest','riot','journalist','conflict','police','activist','law','minister','opposition','military','ban','media','press','legislation','LGBTQI','coup','committee','party','politician','civilian']
#endnumber = ['50','50','25','75','50','50','50','50','50','38','411','983','186','118','114','412','176','77']

for number in range(0, 175, 25):

    for word in keywords:
        url = "https://www.graphic.com.gh/component/search/?searchword=" + word + "&searchphrase=all&start=" + str(number)
        print(url)

        reqs = requests.get(url, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        for link in soup.find_all('a'):
            urls.append(link.get('href')) 
        print(len(urls))

#dftest = pd.DataFrame(list_urls)  
#dftest.to_csv('/Users/diegoromero/Dropbox/GHA_test.csv')  
#print("done!")
urls_unique = list(set(urls))
print(len(urls_unique))
blpatterns = [':80/', '/entertainment/', '/sports/', '/lifestyle/', '/video/', '/opinion/', '/editorials/', '/junior-news/', '/daily-graphic-editorials/', '/features/']

list_urls = []
for url in urls_unique:
    #print(url)
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if url == "#":
                pass
            else:
                if "graphic.com.gh" in url:
                    count_patterns = 0
                    for pattern in blpatterns:
                        if pattern in url:
                            count_patterns = count_patterns + 1
                    if count_patterns == 0:
                        list_urls.append(url)
                else:
                    indexd = url.index("/")
                    if indexd == 0:
                        newurl = "https://www.graphic.com.gh" + url 
                        #print("FIXED: ", newurl)
                        list_urls.append(newurl)


print("Total number of urls found: ", len(list_urls))


## INSERTING IN THE DB:
url_count = 0
for url in list_urls:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if "graphic.com.gh" in url:
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
                    print("newsplease title: ", article['title'])
                    print("newsplease maintext: ", article['maintext'][:50])
 
                    ## Fixing Date:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    try:
                        contains_date = soup.find("time")
                        contains_date = contains_date["datetime"]
                        article_date = dateparser.parse(contains_date, date_formats=['%d/%m/%Y'])
                        article['date_publish'] = article_date
                    except:
                        article_date = article['date_publish']
                        article['date_publish'] = article_date
                    print("newsplease date: ",  article['date_publish'])

                    # Get Main Text:
                    try:
                        maintext_contains = soup.findAll("p")
                        textpieace0 = str(maintext_contains[0].text)
                        if "." in textpieace0:
                            maintext = str(maintext_contains[0].text) + " " + str(maintext_contains[1].text) + " " + str(maintext_contains[2])
                        else:
                            maintext = str(maintext_contains[1].text) + " " + str(maintext_contains[2].text) + " " + str(maintext_contains[3])
                        article['maintext'] = maintext
                    except: 
                        maintext = article['maintext']
                        article['maintext'] = maintext
       
                    #print(article['title'])
                    #print(article['date_publish'])
                    #print(article['maintext']) 

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
                        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        print("DUPLICATE! Not inserted.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
            else:
                pass


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
