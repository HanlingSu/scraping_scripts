
# Packages:
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import re
import dateparser

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []
source = 'news.abamako.com'

base = 'http://news.abamako.com/h/'

url_count = 0
processed_url_count = 0


start = 290902
end = 294725
for i in range(end +1, start, -1):    
    url = base + str(i) + '.html'
    print(url)
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
        article['source_domain'] = source
        print('cutsom parser title ', article['title'] )
        
        
        # custom parser
        soup = BeautifulSoup(response.content, 'html.parser')
    
        # fix date:
        try:
            date = soup.find('div', {"class" : 'FontArticleSource'}).text.split('le')[1].split('|')[0].strip()
            article['date_publish'] = dateparser.parse(date)
        except:
            article['date_publish'] =  None
        print('custom parser date:', article['date_publish'])

        # fix maintext
        try:
            maintext = soup.find('span', {"class" : 'FullArticleTexte'}).text.strip().replace('\n', '')
            article['maintext'] = maintext
        except:
            try:
                maintext = soup.find("meta", {"property":"og:description"})['content']
                article['maintext'] = maintext  
            except: 
                article['maintext']  = None

        print('custom parser maintext', article['maintext'][:50])
        
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
    print('\n',processed_url_count, '/', str(end - start), 'articles have been processed ...\n')


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
