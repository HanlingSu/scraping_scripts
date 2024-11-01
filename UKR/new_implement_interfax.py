'''
created: 2/11/22
author:zung-ru

modified + while loop for failure of request (sleep 10 sec)
'''

import sys
import re
from pymongo import MongoClient
from datetime import datetime, timedelta
import pandas as pd
import requests
from bs4 import BeautifulSoup
# %pip install dateparser
import dateparser
from pymongo.errors import DuplicateKeyError
from tqdm import tqdm
import time


class UpdateDB:

    def __init__(self, col_to_scrape = None,
                        source_domain = None,
                        fix_date_publish = False,
                        fix_title = False,
                        fix_maintext = False,
                        start_year = None, start_month = None):


            self.db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
            self.source_domain = source_domain
            self.dates = pd.date_range(start=datetime(start_year,start_month,1), end=datetime.today(), freq='m')
            self.headers = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            

            if col_to_scrape in ['articles-nodate', 'year_month']:
                self.col_to_scrape = col_to_scrape
            else:
                sys.exit('Error: pick a collection to scrape, either articles-nodate or year_month.')
                # break

            if fix_date_publish in [True, False] and  fix_title in [True, False] and fix_maintext in [True, False]:
                self.fix_date_publish = fix_date_publish
                self.fix_title = fix_title
                self.fix_maintext = fix_maintext
            else:
                sys.exit('Error: assign True/False to fix columns')
                # break

            
########## modify custom parser ############
    def custom_parser(self, doc, soup):
 
        ## fix date
        if self.fix_date_publish:
            try:
                txt = ''
                for s in soup.find_all('script',type="application/ld+json"):
                    txt+=s.string
                    
                date = re.findall('"datePublished": "(.*)",', txt)[0]

                date_publish = dateparser.parse(date, date_formats=['%Y-%m-%dT%H:%M']).replace(tzinfo = None) 
                doc['date_publish'] = date_publish
                print(doc['url'])

            except:
                try:
                    txt =  soup.find( 'div',{'class':"col-18 article-time"})
                    date = ''
                    for i in txt.find_all('span'):
                        date+=i.text+ ' '
                    date_publish = dateparser.parse(date, date_formats=['%Y-%m-%dT%H:%M']).replace(tzinfo = None)
                    doc['date_publish'] = date_publish
                except:
                    doc['date_publish'] = None    ################### if you want to move articles to nodate collection when no date has been collected, 
                                               ##################  otherwise stay in the original collection 
                print(f"No date collected!!!  (url: {doc['url']})")

        ## fix title
        if self.fix_title:
            try:
                str_title = soup.find("meta", {"property":"og:title"})
                title = contains_title['content']
                doc['title'] = title

            except:
                print(f"No title collected!!! (url: {doc['url']})")
            
 
        ## fix maintext        
        if self.fix_maintext:
            try:
                maintext = ''
                j = soup.find('div', {'class':"pdlr15_300"})
                maintext += j.text
                doc['maintext'] = maintext

            except:
                try:
                    maintext = ''
                    j = soup.find('div', {'class':"pdlr15_300"})

                    for i in j.find_all('div'):
                        maintext += i.text

                    doc['maintext'] = maintext

                except:
                    print(f"No maintext collected!!!  (url: {doc['url']})")

            
        return doc


          


    def find_articles(self, date):
        year = date.year
        month = date.month

        colname = f'articles-{year}-{month}'

        cur = self.db[colname].find(
            {
                'source_domain': self.source_domain

            }
        )

        docs = [doc for doc in cur]

        return docs



    
    def update_articles(self, original_date, docs):

    
        for i, doc in enumerate(docs):
            try:   
                try:
                    col_year =  original_date.year
                    col_month = original_date.month
                    colname = f'articles-{col_year}-{col_month}'
                
                except:
                    col_year = None
                    col_month = None
                    colname = 'articles-nodate'

                if self.fix_date_publish:

                    try:
                        if col_year == doc['date_publish'].year and col_month == doc['date_publish'].month:
                            print(f'\n{i+1}: year-month correct, pass!)')
                            pass
                
                        else:
                            try:
                                self.db[colname].delete_one({'_id': doc['_id']})
                            except:
                                print(f'{i+1}: No articles in orginal collection to be deleted')

                            try:
                                col_year =  str(int(doc['date_publish'].year))
                                col_month = str(int(doc['date_publish'].month))
                                colname = f'articles-{col_year}-{col_month}'
                        
                            except:
                                col_year = None
                                col_month = None
                                colname = 'articles-nodate'

                            
                            l = [j for j in self.db[colname].find({'url': doc['url']} )] 
                            if l ==[]:
                                self.db[colname].insert_one(doc)
                            else:
                                print(f'{i+1}: not inserted (for unknown reason)')
                                pass

                    except Exception as err:
                        print(f'{i+1}: Update error: check date if you intended to fix date! (no date collected) ({err})\n(url: {doc["url"]})\n')





                if self.fix_title:

                    self.db[colname].update_one(
                                        {'_id': doc['_id']},
                                        {'$set': {'title': doc['title']}}
                                        )


                if self.fix_maintext:

                    self.db[colname].update_one(
                                        {'_id': doc['_id']},
                                        {'$set': {'maintext': doc['maintext']}}

                
                                    )
            except Exception as err:
                print(f"{i+1}: Update Error: check title/ maintext if you intended to fix title/maintext! ({err})\n(url: {doc['url']})\n")



    def split_list(self, list_to_split, batch_size=20):
        length = len(list_to_split)
        wanted_parts= (length//batch_size)+1
        return [ list_to_split[i*length // wanted_parts: (i+1)*length // wanted_parts] 
                for i in range(wanted_parts) ] 
        



    def main(self):

        if self.col_to_scrape == 'year_month':

            for date in tqdm(self.dates):
                docs = self.find_articles(date)
                list_docs = self.split_list(list_to_split = docs, batch_size=20)
                num_articles =0
                total_articles = len(docs)
                
                for i, batch in enumerate(list_docs):

                    num_articles += len(batch)
                    parsed_batch = []
                    for j, doc in enumerate(batch):

                        url = doc['url']
                        repeat = True
                        count = 0 

                        while repeat:
                            try:
                                req = requests.get(url,headers=self.headers)
                                soup = BeautifulSoup(req.content, features="lxml")
                                repeat=False


                            except Exception as err:
                                repeat = True
                                time.sleep(10)
                                count +=1
                                print(f"Failed to request from web (sleep 10 sec): {err}")
                            
                            if count >= 10:
                                print('Exceeded 10 times requests: pass the url!')
                                print(url)
                                soup=''
                                break

                        if soup != '':
                            doc_parsed = self.custom_parser(doc, soup)
                            #self.update_articles(original_date = date, doc = doc_parsed)
                            parsed_batch.append(doc_parsed)
                        else:
                            continue

                        try:
                            print(f"Batch {i+1}/{len(list_docs)} ({j+1}/{len(batch)}): {date.year}-{date.month} to {doc_parsed['date_publish'].year}-{doc_parsed['date_publish'].month}")
                            print(f"(title) {doc_parsed['title'][:30]} ----  (maintext) {doc_parsed['maintext'][:50]}\n" )
                        except:
                            try:

                                print(f"Batch {i+1}/{len(list_docs)} ({j+1}/{len(batch)}): {date.year}-{date.month} to articles-nodate")
                                print(f"(title) {doc_parsed['title'][:30]} ----  (maintext) {doc_parsed['maintext'][:50]}" )
                                print('Watching out: going to nodate\n')

                            except Exception as err:
                                print(f"title/maintext error: Batch {i+1}/{len(list_docs)} ({j+1}/{len(batch)}) --- {err}\n")
                    
                    self.update_articles(original_date = date, docs = parsed_batch)
                    print(f"\n---- Update completed (batch {i+1}/{len(list_docs)}): {date.year}-{date.month} Total: {num_articles}/{total_articles} ----\n\n")


                    


        elif self.col_to_scrape == 'articles-nodate':

            docs = [doc for doc in self.db['articles-nodate'].find({'source_domain': self.source_domain})]
            list_docs = self.split_list(list_to_split = docs, batch_size=20)
            num_articles =0
            total_articles = len(docs)

            for i, batch in enumerate(list_docs):
                
                num_articles += len(batch)
                parsed_batch = []
                for j, doc in enumerate(batch):

                    url = doc['url']
                    repeat = True
                    count = 0 
                
                    while repeat:
                        try:
                            req = requests.get(url,headers=self.headers)
                            soup = BeautifulSoup(req.content, features="lxml")
                            repeat=False


                        except Exception as err:
                            repeat = True
                            time.sleep(10)
                            count +=1
                            print(f"Failed to request from web (sleep 10 sec): {err}")
                        
                        if count >= 3:
                            print('Exceeded 3 times requests: pass the url!')
                            soup=''
                            break
                        
                    
                    if soup != '':
                        doc_parsed = self.custom_parser(doc, soup)
                        parsed_batch.append(doc_parsed)
                        #self.update_articles(original_date = 'nodate', doc = doc_parsed)

                    else:
                        continue

                    try:
                        print(f"Batch {i+1}/{len(list_docs)} ({j+1}/{len(batch)}): articles-nodate to {doc_parsed['date_publish'].year}-{doc_parsed['date_publish'].month}")
                        print(f"(title) {doc_parsed['title'][:30]} ----  (maintext) {doc_parsed['maintext'][:50]}\n" )
                    except:
                        try:

                            print(f"Batch {i+1}/{len(list_docs)} ({j+1}/{len(batch)}): staying in articles-nodate")
                            print(f"(title) {doc_parsed['title'][:30]} ----  (maintext) {doc_parsed['maintext'][:50]}" )
                            print('Staying in nodate\n\n')

                        except Exception as err:
                            print(f"title/maintext error: Batch {i+1}/{len(list_docs)} ({j+1}/{len(batch)}) --- {err}\n\n")
                
                self.update_articles(original_date = 'nodate', docs = parsed_batch)
                print(f"\n---- Update completed (batch {i+1}/{len(list_docs)}): articles-nodate Total: {num_articles}/{total_articles} ----\n\n")
                    
                
                






if __name__ == "__main__":
    udb = UpdateDB(col_to_scrape = 'year_month',   ## year_month or articles_nodate
                    source_domain = 'interfax.com.ua', 
                    fix_date_publish = True,
                    fix_title = False,
                    fix_maintext = False,
                    start_year = 2022, start_month = 1)

    udb.main()

    
    