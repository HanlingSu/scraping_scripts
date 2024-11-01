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
import json
from newsplease import NewsPlease


class UpdateDB:

    def __init__(self, col_to_scrape = None,
                    domain = None,
                    fix_date_publish = False,
                    fix_title = False,
                    fix_maintext = False,
                    start_year = None):

        

        self.db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
        self.domain = domain
        #change according to your daterange
        self.dates = pd.date_range(start=datetime(start_year,1,1), end=datetime.today(), freq='m')
        #self.dates = pd.date_range(start=datetime(start_year,1,1), end=datetime(start_year,12,31), freq='m')
        print(f'Initializing an instance of the UpdateDB class for {self.domain}.')

        ## Set all the flags.
        if col_to_scrape in ['articles-nodate', 'year_month','wayback']:
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

    def posta_story(self, soup):
        """
        Function to pull the information we want from elfaro.net stories
        :param soup: BeautifulSoup object, ready to parse
        """
        hold_dict = {}
        
        # Get Title: 
        try:
            contains_title = soup.find("meta", {"property":"og:title"})
            article_title = contains_title['content']
            hold_dict['title']  = article_title   

        except:
            article_title = None
            hold_dict['title']  = None
            
        # Get Main Text:
        try:
            maintext_contains = soup.find("meta", {"property":"og:description"})
            maintext_contains = maintext_contains['content']
            hold_dict['maintext'] = maintext_contains
        except: 
            maintext = None
            hold_dict['maintext']  = None

        

    

        # Get Date
        article_date = ''
        try:
            for i in soup.find_all( 'div', {'class':"nd-article__info-block"}):
                date = i.text.splitlines()[1]
            article_date = dateparser.parse(date).replace(tzinfo = None)
            hold_dict['date_publish'] = article_date
        except:
            try:
                s = soup.find('script',type="text/javascript").string
                date = re.findall('"ppublishdate": "(.*)",', s)[0]
                hold_dict['date_publish'] = article_date

                
            except:
                try:
                    s = soup.find('script',type="application/ld+json").string
                    date = re.findall('"datePublished": "(.*)",', s)[0]
                    article_date = dateparser.parse(date).replace(tzinfo = None) 
                    hold_dict['date_publish'] = article_date
                
                except:


                    try: 
                        for i in soup.find_all( 'span', {'class':"news-detail__info__date__item"}):
                            date = str(i.text)
                        article_date = dateparser.parse(date).replace(tzinfo = None)
                        hold_dict['date_publish'] = article_date  
                    except:
                        try:
                            # for i in soup.find_all( 'time'):
                            #     date=i['datetime']
                            # article_date = dateparser.parse(date).replace(tzinfo = None)
                            # hold_dict['date_publish'] = article_date 

                            article_date = None 
                            hold_dict['date_publish'] = article_date
                            print('Custom_parser: Empty date!')
                            
                        except:
                            pass
                                
                            # article_date = None 
                            # hold_dict['date_publish'] = article_date
                            # print('Custom_parser: Empty date!')

    
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
            # Only process if url does not have a blacklisted patter:
            blpatterns = ['/deportes/','/columnas/', '/ef_foto/', '/latienda.', '/ef_academico/', '/ef_tv/', '/ef_radio/', '/cdn-cgi/', '/opinion/', '/fotos/', '/ef_academico/','f_search_scope=','?st-full_text=all&tpl=11','/efradio/','/academico/','salanegra.','elforo.','/el_agora/','/bitacora/']
            count_patterns = 0
            for pattern in blpatterns:
                if pattern in url:
                    count_patterns = count_patterns + 1
            if count_patterns == 0:
                # PROCESSING
                d = self.db[col_name].find_one({'_id' : id})
                if 'web.archive.org' in url and 'https://www.posta.com.tr' in url:
                    final_url = url[url.find('https://www.posta.com.tr'):]
                elif 'web.archive.org' in url and 'http://www.posta.com.tr' in url:
                    final_url = url[url.find('http://www.posta.com.tr'):]
                    

                try:
                    response = requests.get(url, headers=header).text
                    soup = BeautifulSoup(response)
                except:
                    continue

                # Fix maintext, if necessary.
                try:
                    d['maintext'] = self.posta_story(soup)['maintext'] #change
                    print('The manually scraped maintext is ', d['maintext'][0:30])
                except:
                    d['maintext'] = None
                # print('The manually scraped maintext is ', d['maintext'][])

                if d['maintext'] != None and self.fix_maintext == True:
                    m = self.db[col_name].find_one({'_id': d['_id']})
                    self.db[col_name].update_one(
                                            {'_id': d['_id']},
                                            {'$set': {'maintext': d['maintext']}}
                                            )

                # Fix title, if necessary.
                try:
                    d['title'] = self.posta_story(soup)['title'] #change
                    print('The manually scraped title is ', d['title'][0:20])
                except:
                    d['title'] = None

                if d['title'] != None and self.fix_title == True:
                    self.db[col_name].update_one(
                                            {'_id': d['_id']},
                                            {'$set': {'title': d['title']}}
                                            )

                # Fix date_publish, if necessary.
                try:
                    d['date_publish'] = self.posta_story(soup)['date_publish'] #change
                except:
                    d['date_publish'] = None
                print('The manually scraped date_publish is ', d['date_publish'])
                print(d['url'])

                if d['date_publish'] != None and self.fix_date_publish == True:
                    new_year = d['date_publish'].year
                    new_month = d['date_publish'].month
                    d['year'] = new_year
                    d['month'] = new_month
                    new_col_name = f'articles-{new_year}-{new_month}'
                    try:
                        self.db[col_name].delete_one({'url': d['url']})
                        self.db[new_col_name].insert_one(d)
                    except DuplicateKeyError:
                        pass
                elif d['date_publish'] == None and self.fix_date_publish == True:
                    try:
                        self.db[col_name].delete_one({'url': d['url']})
                        self.db['articles-nodate'].insert_one(d)
                    except:
                        pass


            else:
                pass

        print('Update complete.')

    def update_db2(self, l):
        '''
        This is the code that actually does the updating.
        '''
        print('Beginning the actual update.')
        # header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
        header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        lines = l
        data = []
        # year = yr
        # month = mo

        # if year == None:
        #     col_name = f'articles-nodate'
        # else:
        #     col_name = f'articles-{year}-{month}'

        for i, url in enumerate(lines):
            
            # blpatterns = ['/deportes/','/columnas/', '/ef_foto/', '/latienda.', '/ef_academico/', '/ef_tv/', '/ef_radio/', '/cdn-cgi/', '/opinion/', '/fotos/', '/ef_academico/','f_search_scope=','?st-full_text=all&tpl=11','/efradio/','/academico/','salanegra.','elforo.','/el_agora/','/bitacora/']
            # count_patterns = 0
            # for pattern in blpatterns:
            #     if pattern in url:
            #         count_patterns = count_patterns + 1
            # if count_patterns == 0:
            #     # PROCESSING
            #     # d = self.db[col_name].find_one({'_id' : id})
            if 'web.archive.org' in url and 'https://www.posta.com.tr' in url:
                final_url = url[url.find('https://www.posta.com.tr'):]
            elif 'web.archive.org' in url and 'http://www.posta.com.tr' in url:
                final_url = url[url.find('http://www.posta.com.tr'):]
            else:
                final_url = url

                # header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                        
            # print(final_url)
                    

            
            try:
                response = requests.get(final_url, headers=header).text
                d = NewsPlease.from_html(response, url=final_url).__dict__
                soup = BeautifulSoup(response)
            except:
                continue
            

            # Fix maintext, if necessary.
            # try:
            #     d['maintext'] = self.posta_story(soup)['maintext'] #change
            #     print('The manually scraped maintext is ', d['maintext'][0:30])
            # except:
            #     d['maintext'] = None
            # # print('The manually scraped maintext is ', d['maintext'][])

            # if d['maintext'] != None and self.fix_maintext == True:
            #     m = self.db[col_name].find_one({'url': d['url']})
            #     self.db[col_name].update_one(
            #                             {'url': d['url']},
            #                             {'$set': {'maintext': d['maintext']}}
            #                             )

            # Fix title, if necessary.
            # try:
            #     d['title'] = self.posta_story(soup)['title'] #change
            #     print('The manually scraped title is ', d['title'][0:20])
            # except:
            #     d['title'] = None

            # if d['title'] != None and self.fix_title == True:
            #     self.db[col_name].update_one(
            #                             {'url': d['url']},
            #                             {'$set': {'title': d['title']}}
            #                             )

            # Fix date_publish, if necessary.
            try:
                d['date_publish'] = self.posta_story(soup)['date_publish'] #change
                # print(d['date_publish'] )
            except:
                d['date_publish'] = None
            # print(f'({i+1}/{len(lines)}) The manually scraped date_publish is ', d['date_publish'])
            # print(d['url'])

            if d['date_publish'] != None and self.fix_date_publish == True:
                new_year = d['date_publish'].year
                new_month = d['date_publish'].month
                d['year'] = new_year
                d['month'] = new_month
                new_col_name = f'articles-{new_year}-{new_month}'
                try:
                    try:
                        self.db[new_col_name].delete_one({'url': d['url']})
                        
                    except:
                        pass
                    self.db[new_col_name].insert_one(d)
                    print(f"Insert: ({i+1}/{len(lines)}) date ----- {d['date_publish']} ----- {d['url']} ",'\n')

                except DuplicateKeyError:
                    
                    pass
            elif d['date_publish'] == None and self.fix_date_publish == True:
                try:
                    self.db[new_col_name].delete_one({'url': d['url']})
                    self.db['articles-nodate'].insert_one(d)
                    print(f"Insert: ({i+1}/{len(lines)}) date ----- Nodate ----- {d['url']} ",'\n')
                except:
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
                    #'url': {'$not': re.compile('web.archive.org', re.IGNORECASE)},
                    #'url': {'$regex': '/international/'},
                    #'download_via': {'$in': [None, '']},
                    #'download_via': 'direct',
                    'source_domain' : self.domain,
                    'include':{'$exists':False}
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
        if self.col_to_scrape == 'wayback':
            fromdate = "20220501" 

            todate = "20220930"     

            sources = ['posta.com.tr']

            for source in sources:
                url = "https://web.archive.org/cdx/search/cdx?url=" + source + "&matchType=domain&collapse=urlkey&from=" + fromdate + "&to=" + todate + "&output=json"

                urls = requests.get(url).text
                parse_url = json.loads(urls) #parses the JSON from urls.

                print("Working on ", len(parse_url), "urls from Wayback Machine's archive for", source)
                url_list = []
                final_url_list = []
                for i in range(1,len(parse_url)):
                    
                    if str(parse_url[i][4]) == "200":
                        orig_url = parse_url[i][2]
                        if orig_url == "https://www." + source + "/":
                            # url_list.append(final_url)
                            pass
                        else:
                            if orig_url == "https://" + source + "/":
                                pass
                            else:
                                tstamp = parse_url[i][1]
                                waylink = tstamp+'/'+orig_url
                                ## Compiles final url pattern:
                                final_url = 'https://web.archive.org/web/' + waylink
                                
                                url_list.append(final_url)

                bl = ['/bugun-ne-pisirsem-diyenlere-gunun-menusu', '/burclarin-sans-ve-para-durumu,', '/burclarin-sans-ve-para-durumu', '/galeri/', '/video/', '/sampiy10/', '/yazarlar/', '/img/', '/video-havuzu/', '/arama?q=', '/advertorial/', '/anne-cocuk/', '/amp/','/video.posta.com/']

                
                
                for url in url_list:
                    if not any(ext in url for ext in bl) and 'www.posta.com.tr' in url:
                        print(url)
                        final_url_list.append(url)

                final_url_list = final_url_list

                    
                print("Working on ", len(final_url_list), "urls from Wayback Machine's archive for", source)

                self.update_db2(final_url_list)





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
    udb = UpdateDB(col_to_scrape = 'wayback',
                    domain = 'posta.com.tr',
                    fix_date_publish = True,
                    fix_title = False,
                    fix_maintext = False,
                    start_year = 2022)
    udb.main()