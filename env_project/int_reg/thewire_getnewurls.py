# Packages:
from typing import final
from unicodedata import category
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import dateparser
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import re
import json
import time
import pandas as pd


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
source = 'thewire.in'

# selenium scraping script


    # pages = [5, 5]
    # # screen_height = driver.execute_script("return window.screen.height;")   # get the screen height of the web
    # # sleep_time = 1

    # direct_URLs = set()
    # page = 0

    # url = 'https://thewire.in/category/science/all'
    # driver = webdriver.Chrome() 


    # print(url)
    # driver.get(url)    
    # time.sleep(3)
    # while page<100000:
    #     try:
    #         # driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    #         xpath = '/html/body/div[1]/div/div[1]/div[3]/div[1]/div[4]/div/div[3]'
    #         element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    #         driver.execute_script("arguments[0].scrollIntoView();", element)
            
    #         element.click()  
    #         driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    #         time.sleep(2)

    #         page+=1
    #         print('Page {}'.format(page))
            
            
    #     except:
    #         # Break if button is not found
    #         driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            
    #         # page+=1
    #         print('No button')
    #         pass
    #         #Give enough time for button and urls to appear
        
    #     if page % 5 == 0:
    #         try:
    #             soup = BeautifulSoup(driver.page_source, 'html.parser')

    #             # print(soup)
    #             for item in soup.find_all('div', {'class' : 'side-article-title-mc'}):
    # #                 print(item)
    #                 try:
    #                     direct_URLs.add(item.find('a')['href'])
    #                 except:
    #                     pass
    #                     print("no item")
    #             print(len(direct_URLs))
                
    #         except:
    #             print('No soup')
    #         time.sleep(3)
    # try:
    #     soup = BeautifulSoup(driver.page_source, 'html.parser')
    #     for item in soup.find_all('article'):
    # #                 print(item)
    #         direct_URLs.add(item.find('a')['href'])
        
    #     print(len(direct_URLs))
        
    # except:
    #     print('No soup')
            
    # direct_URLs = ['https://thewire.in' + i for i in  direct_URLs]

final_result = pd.read_csv("Downloads/peace-machine/peacemachine/getnewurls/env_project/int_reg/thewire.csv")['0']

url_count = 0
processed_url_count = 0
final_result_len = 0
    

print(len(final_result))
final_result_len += len(final_result)

for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            response = requests.get(url, headers=header)
            # process
            article = NewsPlease.from_html(response.text, url=url).__dict__
            soup = BeautifulSoup(response.content, 'html.parser')

            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            article['url'] = url
            article['environmental'] = True

            ## Fixing maintext:     
            try:
                maintext = json.loads(soup.find_all('script',{'type':"application/ld+json"})[1].contents[0])['articleBody']
                article['maintext'] = maintext
            except:
                article['maintext'] = article['maintext']         
            
            try:
                date = soup.find('meta', {'name' :'article:published_date'})['conent']
                article['date_publish'] = dateparser.parse(date)
            except:
                date = json.loads(soup.find_all('script',{'type':"application/ld+json"})[1].contents[0])['datePublished']
                article['date_publish'] = dateparser.parse(date)

            if article['maintext']:
                print("newsplease maintext: ", article['maintext'][:50])
            print("newsplease date: ", article['date_publish'])
            print("newsplease title: ", article['title'])

            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'articles-{year}-{month}'
                #print(article)
            except:
                colname = 'articles-nodate'
            #print("Collection: ", colname)
            try:
                
                db[colname].insert_one(article)
                # count:
                if colname!= 'articles-nodate':
                    url_count = url_count + 1
                    print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                    db['urls'].insert_one({'url': article['url']})
            except DuplicateKeyError:
                print("DUPLICATE! Not inserted.")
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', final_result_len, 'articles have been processed ...\n')

    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
