"""
Created on Tue Aug 31 

Modified: zung-ru
"""
import sys
import re
from pip import main
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import dateparser
from pymongo.errors import DuplicateKeyError
from tqdm import tqdm
from time import sleep
import re
import sys

class UpdateDB:

    def __init__(self, col_to_scrape = None,
                    domain = None,
                    fix_date_publish = False,
                    fix_title = False,
                    fix_maintext = False,
                    start_year = None):

        '''
        Author: Tim McDade and Akanksha Bhattacharyya
        Date: 20 April 2021
        Modified by Diego Romero (June 8, 2021)
        '''

        self.db = MongoClient('mongodb://ml4pAdmin:ml4peace@research-devlab-mongodb-01.oit.duke.edu').ml4p
        self.domain = domain
        #change according to your daterange
        #self.dates = pd.date_range(start=datetime(start_year,1,1), end=datetime(start_year,1,31), freq='m')
        self.dates = pd.date_range(start=datetime(start_year,5,1), end=datetime(2022,7,31), freq='m')
        print(f'Initializing an instance of the UpdateDB class for {self.domain}.')

        ## Set all the flags.
        if col_to_scrape in ['articles-nodate', 'year_month']:
            self.col_to_scrape = col_to_scrape
        else:
            sys.exit('Error: pick a collection to scrape, either articles-nodate or year_month.')
            # break

        if fix_date_publish in [True, False]:
            self.fix_date_publish = fix_date_publish
        else:
            sys.exit('Error: pick whether fix_date_publish is True or False.')
            # break

        if fix_title in [True, False]:
            self.fix_title = fix_title
        else:
            sys.exit('Error: pick whether fix_title is True or False.')
            # break

        if fix_maintext in [True, False]:
            self.fix_maintext = fix_maintext
        else:
            sys.exit('Error: pick whether fix_maintext is True or False.')
            # break



#################
# Custom Parser #
#################

    def moscowtimes_story(self, soup):

        """
        Function to pull the information we want from moscowtimes stories
        :param soup: BeautifulSoup object, ready to parse
        """
        hold_dict = {}
        
        # Get Title: 
        try:
            article_title = soup.find('meta', property="og:title")['content'].replace('- The Moscow Times', '')
            hold_dict['title']  = article_title   
    
        except:
            article_title = None
            hold_dict['title']  = None
            

        # Get Main Text:
        try:
        
            soup.find_all('p')
            maintext = ''
            for i in soup.find_all('p'):
                maintext += i.text
            if 'pm' in maintext :
                maintext = maintext.split('pm', 1)[-1]
            elif  'am' in maintext:
                maintext = maintext.split('am', 1)[-1]
            else:
                maintext = maintext
            hold_dict['maintext'] = maintext.strip()              
        except:
            maintext = None
            hold_dict['maintext']  = None
                            
          
            
    

        # Get Date
        try:
            date = soup.find('meta', property = 'article:published_time')['content']
            hold_dict['date_publish'] = dateparser.parse(date).replace(tzinfo = None) 

        except:
            date = None 
            hold_dict['date_publish'] = None

        return hold_dict 
           



    def update_db(self, l, yr, mo):
        '''
        This is the code that actually does the updating.
        '''
        print('Beginning the actual update.')
        # header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
        header = {'User-Agent': 'Mozilla/5.0'}
        lines = l
        data = []
        year = yr
        month = mo

        if year == None:
            col_name = f'articles-nodate'
        else:
            col_name = f'articles-{year}-{month}'

        for url,id in tqdm(lines):
            # USING requests and b4 scraper
            req = requests.get(url, headers=header)
            soup = BeautifulSoup(req.content)

            
            print(url)

            d = self.db[col_name].find_one({'_id' : id})
            if type(d)!=dict:
                continue

            try:
                d['maintext'] =  self.moscowtimes_story(soup)['maintext']
            except:
                d['maintext'] = None
             

            

            if d['maintext'] == None and self.fix_maintext == True:
                m = self.db[col_name].find_one({'_id': d['_id']})
                self.db[col_name].update_one(
                                        {'_id': d['_id']},
                                        {'$set': {'maintext': d['maintext']}}
                                        )
                print('Empty maintext content!')

            if d['maintext'] != None and self.fix_maintext == True:
                m = self.db[col_name].find_one({'_id': d['_id']})
                self.db[col_name].update_one(
                                        {'_id': d['_id']},
                                        {'$set': {'maintext': d['maintext']}}
                                        )
                print(d['maintext'][:50])
                print('Maintext modified!')



            # Fix title, if necessary.
            try:
                d['title'] = self.moscowtimes_story(soup)['title'] #change
            except:
                d['title'] = None
            # print('The manually scraped title is ', d['title'])

            if d['title'] != None and self.fix_title == True:
                self.db[col_name].update_one(
                                        {'_id': d['_id']},
                                        {'$set': {'title': d['title']}}
                                        )
                print("Title modified! ", d['title'])


            # Fix date_publish, if necessary.
            try:
                d['date_publish'] = self.moscowtimes_story(soup)['date_publish'] #change
            except:
                d['date_publish'] = None
            print('The manually scraped date_publish is: ', d['date_publish'])

            if d['date_publish'] == None and self.fix_date_publish == True: 
                self.db[col_name].delete_one({'url': d['url']})
                self.db['articles-nodate'].insert_one(d)
                print("Inserted in articles-nodate.")

            if d['date_publish'] != None and self.fix_date_publish == True:
                new_year = d['date_publish'].year
                new_month = d['date_publish'].month
                d['year'] = new_year
                d['month'] = new_month
                new_col_name = f'articles-{new_year}-{new_month}'
                try:
                    self.db[col_name].delete_one({'url': d['url']})
                    self.db[new_col_name].insert_one(d)
                    print("Inserted in {}.".format(new_col_name))
                except DuplicateKeyError:
                    self.db[col_name].delete_one({'url': d['url']})
                    self.db[new_col_name].delete_one({'url': d['url']})
                    self.db[new_col_name].insert_one(d)
                    print('Duplicated URL, updated!')
                    pass
                    
        print('Update complete.')


    #########################################
    # Change with respect to sub collection #
    #########################################

    def find_articles(self, url, year, month,
                                col_name,
                                title_filter_string = 'Página no encontrada',
                                maintext_filter_string = ''):
        '''
        This updates the articles in the collection with col_name and satisfy following conditions.
        '''
        print('Finding the articles to be updated.')
        # col_name = f'articles-nodate'
        query = {
                    # {'$or': [{'title' : {'$regex' : re.compile(title_filter_string, re.IGNORECASE)}},
                    #          {'maintext' : {'$regex' : re.compile(maintext_filter_string, re.IGNORECASE)}}]},
                    # 'title' : {'$regex' : re.compile(title_filter_string, re.IGNORECASE)},
                    #'title' : {'$in' : ['', None]},
                    ## Find all articles where the title/maintext is empty or
                    ## where the title/maintext contains some string
                    # 'title' :{"$regex": '/^.{100,}$/'},
                    # 'url': {'$not': re.compile('/archive.html', re.IGNORECASE)},
                    # 'download_via': {'$in': [None, '']},
                    # 'url': {'$regex': 'themoscowtimes.com'}
                    'source_domain' : self.domain,
                    'maintext' : {'$regex' : '^[0-9].*'}
                    # 'year' : 2017,
                    # 'month':1
                }
        to_update = [x for x in self.db[col_name].find(query)]
        # d = [(i['url'], i['_id']) for i in self.db[col_name].find({'source_domain': self.domain})]
        d = [(i['url'], i['_id']) for i in tqdm(to_update)]
        print('{} articles found.'.format(len(to_update)))
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
        
#############################
# Implement custom scraping #
#############################

if __name__ == "__main__":
    udb = UpdateDB(col_to_scrape = 'year_month',
                    domain = 'utusan.com.my',
                    fix_date_publish = False,
                    fix_title = False,
                    fix_maintext = True,
                    start_year = 2021)
    udb.main()