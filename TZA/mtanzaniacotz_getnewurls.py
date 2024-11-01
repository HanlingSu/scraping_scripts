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
import cloudscraper

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []

categories = ['kitaifa', 'habari-kuu', 'kimataifa', 'makala', 'uchumi', 'siasa', 'afya']
            #  national,  main news,  international, articles, economy, politics, health and community,         
                                                    ##
page_start = [1, 1, 1, 1, 1, 1, 1]
page_end = [32, 6, 1, 2, 17, 2, 15]

url = 'https://mtanzania.co.tz/category/'


scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'firefox',
        'platform': 'windows',
        'mobile': False
    }
)


for c, ps, pe in zip(categories, page_start, page_end):
    for p in range(ps, pe+1):
        # mundo, nacionales, noticias-del-dia, espectaculos, ciencia
        link = url + c + '/page/' + str(p)
        print(link)
        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
        soup = BeautifulSoup(scraper.get(link).text, 'html.parser')
        
        items = soup.find_all('div', {'class' :'tdb_module_loop td_module_wrap td-animation-stack td-cpt-post'})
        for i in items:
            for j in i.find_all('p', {'class' : 'entry-title td-module-title'}):
                direct_URLs.append(j.find('a')['href'])

        print(len(direct_URLs))


final_result = list(set(direct_URLs))
print(len(final_result))

url_count = 0
processed_url_count = 0
source = 'mtanzania.co.tz'
for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            response = scraper.get(url)
            # process
            soup = BeautifulSoup(response.text, 'html.parser')
           
            article = NewsPlease.from_html(response.text, url=url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            # add language code
            article['language'] = 'sw'
            print("newsplease title: ", article['title'])
            print("newsplease date: ",  article['date_publish'])
#             print("newsplease maintext: ", article['maintext'][:50])
            

            # custom parser
            soup = BeautifulSoup(scraper.get(url).text, 'html.parser')
            
                
            # fix main text
            try:
                soup.find('div', {'class' :'td_block_wrap tdb_single_content tdi_127 td-pb-border-top td_block_template_1 td-post-content tagdiv-type'}).find('div', {'class' :'tdb-block-inner td-fix-index'}).find_all('p')
                maintext = ''
                for i in soup.find('div', {'class' :'td_block_wrap tdb_single_content tdi_127 td-pb-border-top td_block_template_1 td-post-content tagdiv-type'}).find('div', {'class' :'tdb-block-inner td-fix-index'}).find_all('p'):
                    maintext += i.text +' '
                article['maintext'] = maintext.strip()
            except:
                try:
                    maintext = soup.find('div', {'class' :'td_block_wrap tdb_single_content tdi_127 td-pb-border-top td_block_template_1 td-post-content tagdiv-type'}).find('div', {'class' :'tdb-block-inner td-fix-index'}).find_all('p').text.strip()
                    article['maintext'] = maintext
                except:
                    article['maintext'] = article['maintext'] 
            if article['maintext']:
                print("newsplease maintext: ", article['maintext'][:50])
            
            
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'articles-{year}-{month}'
                
            except:
                colname = 'articles-nodate'
            
            # Inserting article into the db:
            try:
                db[colname].insert_one(article)
                # count:
                if colname != 'articles-nodate':
                    url_count = url_count + 1
                    print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                db['urls'].insert_one({'url': article['url']})
            except DuplicateKeyError:
                pass
                print("DUPLICATE! Not inserted.")
                
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
                    
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
