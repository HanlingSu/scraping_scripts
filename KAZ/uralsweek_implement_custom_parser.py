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
                    fix_date_publish = False,
                    fix_title = False,
                    fix_maintext = False,
                    start_year = None):

        '''
        Author: Tim McDade and Akanksha Bhattacharyya
        Date: 20 April 2021
        Modified by Diego Romero (Mar 28, 2023)
        '''

        self.db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
        self.domain = domain
        #change according to your daterange
        self.dates = pd.date_range(start=datetime(start_year,4,1), end=datetime.today(), freq='m')
        #self.dates = pd.date_range(start=datetime(start_year,5,31), end=datetime(start_year,6,30), freq='m')
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

    ###########################################################
    def uralskweekkz_story(self, soup):
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
            print(url, " ", len(url))
            # Delete useless URLS
            d = self.db[col_name].find_one({'_id' : id})
            response = requests.get(url, headers=header).text
            soup = BeautifulSoup(response)

            if len(url) <= 40:
                print("DELETING: ", url)
                self.db[col_name].delete_one({'url': d['url']})
            else:
                if "/page/" in url:
                    print("DELETING: ", url)
                    self.db[col_name].delete_one({'url': d['url']})
                else:
                    print("Working on: ", url)
                    # Fix date_publish, if necessary.
                    try:
                        new_text = self.uralskweekkz_story(soup)['maintext'] #change
                    except:
                        new_text = None
                            
                    if self.fix_maintext == True:
                        if new_text == None:
                            print("+ Maintext: NONE.")
                        else:
                            print("+ Maintext: ", new_text[0:100])
                        d['maintext'] = new_text
                        self.db[col_name].delete_one({'url': d['url']})
                        self.db[col_name].insert_one(d)
                    else:
                        pass
        print('Update complete.')

    # def find_article_with_date(self, url, year, month):
    #     '''
    #     This updates the articles in the collection specific to a particular month.
    #     '''
    #     col_name = f'articles-{year}-{month}'
    #     d = [(i['url'], i['_id']) for i in self.db[col_name].find({'source_domain': self.domain})]
    #     return d


    def find_articles(self, url, year, month,
                                col_name,
                                title_filter_string = 'Página no encontrada',
                                maintext_filter_string = 'Please enter an answer in'):
        '''
        This updates the articles in the articles-nodate collection.
        '''
        print('Finding the articles to be updated.')
        # col_name = f'articles-nodate' 	 

        query = {
                    #{'$or': [{'title' : {'$regex' : re.compile(title_filter_string, re.IGNORECASE)}},
                    #          {'maintext' : {'$regex' : re.compile(maintext_filter_string, re.IGNORECASE)}}]},
                    # 'title' : {'$regex' : re.compile(title_filter_string, re.IGNORECASE)},
                    #'maintext' : {'$regex': 'bg_error_lines'},
                    ## Find all articles where the title/maintext is empty or
                    ## where the title/maintext contains some string
                    #'title' : {'$in': [None, re.compile(title_filter_string, re.IGNORECASE)]},
                    #'url': {'$not': re.compile('/amp/', re.IGNORECASE)},
                    #'url': {'$regex': '/kz/'},
                    #'download_via': {'$in': ['gdelt','wayback_alt','wayback','',None]},
                    #'download_via': 'direct',
                    #'maintext': {'$in': [None, '',' ','  ','    ']},
                    #'title':{'$not': re.compile('IIS 8.5 Detailed Error - 404.0 - Not Found', re.IGNORECASE)},
                    'maintext' : {'$regex': 'Please enter an answer in'},
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
            l = self.find_articles(rgx, 2020, 3, col_name = col_name,
                                title_filter_string = '',
                                maintext_filter_string = '')
            self.update_db(l, None, None)

        print(f'All done with {self.domain}.')

if __name__ == "__main__":
    udb = UpdateDB(col_to_scrape = 'year_month',
                    domain = 'uralskweek.kz',
                    fix_date_publish = False,
                    fix_title = False,
                    fix_maintext = True,
                    start_year = 2023)
    udb.main()