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



class UpdateDB:

    def __init__(self, col_to_scrape = None,
                    domain = None,
                    fix_lanlab = False,
                    start_year = None):

        '''
        Author: Tim McDade and Akanksha Bhattacharyya
        Date: 20 April 2021
        Modified by Diego Romero (Dec 22, 2021)
        '''

        self.db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
        self.domain = domain
        #change according to your daterange
        self.dates = pd.date_range(start=datetime(start_year,9,1), end=datetime.today(), freq='m')
        #self.dates = pd.date_range(start=datetime(start_year,1,1), end=datetime(2021,2,28), freq='m')
        print(f'Initializing an instance of the UpdateDB class for {self.domain}.')

        ## Set all the flags.
        if col_to_scrape in ['articles-nodate', 'year_month']:
            self.col_to_scrape = col_to_scrape
        else:
            sys.exit('Error: pick a collection to scrape, either articles-nodate or year_month.')
            # break

        if fix_lanlab in [True, False]:
            self.fix_lanlab = fix_lanlab
        else:
            sys.exit('Error: pick whether fix_lanlab is True or False.')
            # break

    def update_db(self, l, yr, mo):
        '''
        This is the code that actually does the updating.
        '''
        print('Beginning the actual update.')
        header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
        lines = l
        data = []
        year = yr
        month = mo

        if year == None:
            col_name = f'articles-nodate'
        else:
            col_name = f'articles-{year}-{month}'

        for url,id in tqdm(lines):
            #print(url)
            # FIX URL
            #indexgraphic = url.find("/blog/")
            #newurl = "http://www.therwandan.com/" + url[(indexgraphic + 6):]  
            #print(newurl)

            d = self.db[col_name].find_one({'_id' : id})
            

            # Fix language label:
 
            if d['language'] == 'en' and self.fix_lanlab == True:
                if '/sq/' in url:
                    d['language'] = 'sq'
                    self.db[col_name].update_one({'_id': d['_id']},{'$set': {'language': d['language']}})
                else:
                    if '?lang=sq' in url:
                        d['language'] = 'sq'
                        self.db[col_name].update_one({'_id': d['_id']},{'$set': {'language': d['language']}})
                    else:
                        if '/sr/' in url:
                            d['language'] = 'sr'
                            self.db[col_name].update_one({'_id': d['_id']},{'$set': {'language': d['language']}})
                        else:
                            if '?lang=sr' in url:
                                d['language'] = 'sr'
                                self.db[col_name].update_one({'_id': d['_id']},{'$set': {'language': d['language']}})
                            else:
                                if '/hu/' in url:
                                    d['language'] = 'hu'
                                    self.db[col_name].update_one({'_id': d['_id']},{'$set': {'language': d['language']}})
                                else:
                                    if '?lang=hu' in url:
                                        d['language'] = 'hu'
                                        self.db[col_name].update_one({'_id': d['_id']},{'$set': {'language': d['language']}})
                                    else:
                                        if '/uk/' in url:
                                            d['language'] = 'uk'
                                            self.db[col_name].update_one({'_id': d['_id']},{'$set': {'language': d['language']}})
                                        else:
                                            if '?lang=uk' in url:
                                                d['language'] = 'uk'
                                                self.db[col_name].update_one({'_id': d['_id']},{'$set': {'language': d['language']}})
                                            else:
                                                if '/el/' in url:
                                                    d['language'] = 'el'
                                                    self.db[col_name].update_one({'_id': d['_id']},{'$set': {'language': d['language']}})
                                                else:
                                                    if '?lang=el' in url:
                                                        d['language'] = 'el'
                                                        self.db[col_name].update_one({'_id': d['_id']},{'$set': {'language': d['language']}})
            else:
                pass

        print('Update complete.')


    def find_articles(self, url, year, month,
                                col_name,
                                title_filter_string = 'Página no encontrada',
                                maintext_filter_string = ''):
        '''
        This updates the articles in the articles-nodate collection.
        '''
        print('Finding the articles to be updated.')
        # col_name = f'articles-nodate'
        query = {
                    'source_domain' : self.domain
                }
        to_update = [x for x in self.db[col_name].find(query)]
        # d = [(i['url'], i['_id']) for i in self.db[col_name].find({'source_domain': self.domain})]
        d = [(i['url'], i['_id']) for i in tqdm(to_update)]
        print('Articles found.')
        return d


    def main(self):
        '''
        This code runs the updates for whichever collection is supposed
        to be updated, according to the field self.col_to_scrape.
        '''
        #### if custom scraping 'articles-{year}-{month}'  collection
        if self.col_to_scrape == 'year_month':
            rgx = ''
            for date in tqdm(self.dates):
                year = date.year
                month = date.month
                col_name = f'articles-{year}-{month}'
                # l = find_articles(rgx, year, month) #change
                l = self.find_articles(rgx, year, month, col_name = col_name,
                                title_filter_string = '',
                                maintext_filter_string = '')
                self.update_db(l, year, month)
                print(col_name)

        #### if custom scraping 'articles-nodate'  collection
        elif self.col_to_scrape == 'articles-nodate':
            rgx = ''
            col_name = self.col_to_scrape
            l = self.find_articles(rgx, 2021, 3, col_name = col_name,
                                title_filter_string = '',
                                maintext_filter_string = '')
            self.update_db(l, None, None)

        print(f'All done with {self.domain}.')

if __name__ == "__main__":
    udb = UpdateDB(col_to_scrape = 'year_month',
                    domain = 'balkaninsight.com',
                    fix_lanlab = True,
                    start_year = 2022)
    udb.main()