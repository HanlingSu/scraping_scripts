## Fixing dates for abamako

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
        Modified by Diego Romero (Aug 30, 2022)
        '''

        self.db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
        self.domain = domain
        #change according to your daterange
        self.dates = pd.date_range(start=datetime(start_year,6,30), end=datetime.today(), freq='m')
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

    def newsabamakocom_story(self, soup):
        """
        Function to pull the information we want from news.abamako.com stories
        :param soup: BeautifulSoup object, ready to parse
        """
        hold_dict = {}

        # Get Title: 
        try:
            contains_title = soup.find("meta", {"property":"og:title"})
            article_title = contains_title['content']
            hold_dict['title']  = article_title   
        except:
            try:
                contains_title = soup.find("title")
                article_title = contains_title.text
                hold_dict['title']  = article_title  
            except:
                hold_dict['title']  = None
            
        # Get Main Text:
        try:
            contains_text = soup.findAll('span',{"class":"FullArticleTexte"})
            if len(contains_text) > 1:
                if len(contains_text) == 2:
                    maintext = contains_text[0].text + contains_text[1].text
                else:
                    maintext = contains_text[0].text + contains_text[1].text + contains_text[2].text
            else:
                maintext = contains_text[0].text
            hold_dict['maintext'] = maintext
        except: 
            try:
                contains_maintext = soup.find("meta", {"property":"og:description"})
                maintext = contains_maintext['content']
                hold_dict['maintext'] = maintext  
            except: 
                maintext = None
                hold_dict['maintext']  = None

        # Get Date
        try: 
            months = ['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre']
            months2 = ['janvier','fevrier','mars','avril','mai','juin','juillet','aout','septembre','octobre','novembre','decembre']
            try: 
                contains_date = soup.find("div", {"class":"FontArticleSource"}).text

                if "/201" in contains_date:
                    contains_datelist = contains_date.split()
                    for i in contains_datelist:
                        if "/201" in i:
                            indexdate = contains_datelist.index(i)
                    datebit = contains_datelist[indexdate]
                    datebit = datebit.replace("/", " ")
                    datevector = datebit.split()
                    dayx = datevector[0]
                    monthx = datevector[1]
                    yearx = datevector[2]
                    article_date = datetime(int(yearx),int(monthx),int(dayx))
                    hold_dict['date_publish'] = article_date
                else:
                    if "/202" in contains_date:
                        contains_datelist = contains_date.split()
                        for i in contains_datelist:
                            if "/202" in i:
                                indexdate = contains_datelist.index(i)
                        datebit = contains_datelist[indexdate]
                        datebit = datebit.replace("/", " ")
                        datevector = datebit.split()
                        dayx = datevector[0]
                        monthx = datevector[1]
                        yearx = datevector[2]
                        article_date = datetime(int(yearx),int(monthx),int(dayx))
                        hold_dict['date_publish'] = article_date
                    else:
                        contains_datelist = contains_date.split()
                        for i in contains_datelist:
                            if "201" in i:
                                indexdate = contains_datelist.index(i)
                            else:
                                if "202" in i:
                                    indexdate = contains_datelist.index(i)
                        yearx = contains_datelist[indexdate] 
                        dayx = contains_datelist[indexdate-2] 
                        montht = contains_datelist[indexdate-1] 
                        montht = montht.lower()
                        if montht in months:
                            monthx = months.index(montht) + 1
                        else:
                            monthx = months2.index(montht) + 1
                        article_date = datetime(int(yearx),int(monthx),int(dayx))
                        hold_dict['date_publish'] = article_date
            except:
                contains_date_list = soup.findAll("div", {"class":"FontArticleSource"})
                contains_date = contains_date_list[1].text
                if "/201" in contains_date:
                    contains_datelist = contains_date.split()
                    for i in contains_datelist:
                        if "/201" in i:
                            indexdate = contains_datelist.index(i)

                    datebit = contains_datelist[indexdate]
                    datebit = datebit.replace("/", " ")
                    datevector = datebit.split()
                    dayx = datevector[0]
                    monthx = datevector[1]
                    yearx = datevector[2]
                    article_date = datetime(int(yearx),int(monthx),int(dayx))
                    hold_dict['date_publish'] = article_date
                else:
                    if "/202" in contains_date:
                        contains_datelist = contains_date.split()
                        for i in contains_datelist:
                            if "/202" in i:
                                indexdate = contains_datelist.index(i)

                        datebit = contains_datelist[indexdate]
                        datebit = datebit.replace("/", " ")
                        datevector = datebit.split()
                        dayx = datevector[0]
                        monthx = datevector[1]
                        yearx = datevector[2]
                        article_date = datetime(int(yearx),int(monthx),int(dayx))
                        hold_dict['date_publish'] = article_date
                    else:
                        contains_datelist = contains_date.split()
                        for i in contains_datelist:
                            if "201" in i:
                                indexdate = contains_datelist.index(i)
                            else:
                                if "202" in i:
                                    indexdate = contains_datelist.index(i)
                        yearx = contains_datelist[indexdate] 
                        dayx = contains_datelist[indexdate-2] 
                        montht = contains_datelist[indexdate-1] 
                        montht = montht.lower()
                        monthx = months.index(montht) + 1
                        article_date = datetime(int(yearx),int(monthx),int(dayx))
                        hold_dict['date_publish'] = article_date
        except:
            article_date = None
            hold_dict['date_publish'] = None  
    
        return hold_dict 



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
            response = requests.get(url, headers=header).text
            soup = BeautifulSoup(response)

            # Fix maintext, if necessary.
            try:
                d['maintext'] = self.newsabamakocom_story(soup)['maintext'] #change
                #print('The manually scraped maintext is ', d['maintext'][0:50])
            except:
                d['maintext'] = None
            
            if d['maintext'] != None and self.fix_maintext == True:
                m = self.db[col_name].find_one({'_id': d['_id']})
                self.db[col_name].update_one(
                                        {'_id': d['_id']},
                                        {'$set': {'maintext': d['maintext']}}
                                        )

            # Fix title, if necessary.
            try:
                d['title'] = self.newsabamakocom_story(soup)['title'] #change
            except:
                d['title'] = None
            # print('The manually scraped title is ', d['title'])

            if d['title'] != None and self.fix_title == True:
                self.db[col_name].update_one(
                                        {'_id': d['_id']},
                                        {'$set': {'title': d['title']}}
                                        )

            # Fix date_publish, if necessary.
            original_date = d['date_publish']

            try:
                new_date = self.newsabamakocom_story(soup)['date_publish'] #change
            except:
                new_date = None

            if new_date != None and self.fix_date_publish == True:
                if new_date != original_date:
                    d['date_publish'] = new_date
                    new_year = d['date_publish'].year
                    new_month = d['date_publish'].month
                    d['year'] = new_year
                    d['month'] = new_month
                    new_col_name = f'articles-{new_year}-{new_month}'
                    try:
                        self.db[col_name].delete_one({'url': d['url']})
                        self.db[new_col_name].insert_one(d)
                        print("WRONG! Correct date is: ",new_date, " -- ", url)
                    except DuplicateKeyError:
                        self.db[col_name].delete_one({'url': d['url']})
                        print("WRONG! Correct date is: ",new_date, " -- ", url)
                else:
                    #pass
                    print("Correct date is: ",original_date, " -- ", url)
            #print('The manually scraped date_publish is ', d['date_publish'])


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
                                maintext_filter_string = ''):
        '''
        This updates the articles in the articles-nodate collection.
        '''
        print('Finding the articles to be updated.')
        # col_name = f'articles-nodate'
        query = {
                    # {'$or': [{'title' : {'$regex' : re.compile(title_filter_string, re.IGNORECASE)}},
                    #          {'maintext' : {'$regex' : re.compile(maintext_filter_string, re.IGNORECASE)}}]},
                    # 'title' : {'$regex' : re.compile(title_filter_string, re.IGNORECASE)},
                    #'maintext' : {'$regex': 'bg_error_lines'},
                    ## Find all articles where the title/maintext is empty or
                    ## where the title/maintext contains some string
                    #'title' : {'$in': [None, re.compile(title_filter_string, re.IGNORECASE)]},
                    #'url': {'$not': re.compile('/amp/', re.IGNORECASE)},
                    #'url': {'$regex': '/details/article/'},
                    #'download_via': {'$in': ['gdelt','wayback_alt','wayback','',None]},
                    #'download_via': 'direct',
                    #'maintext': {'$in': [None, '',' ','  ','    ']},
                    #'title':{'$not': re.compile('IIS 8.5 Detailed Error - 404.0 - Not Found', re.IGNORECASE)},
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
                    domain = 'news.abamako.com',
                    fix_date_publish = True,
                    fix_title = False,
                    fix_maintext = False,
                    start_year = 2012)
    udb.main()