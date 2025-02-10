# Packages:

from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from pymongo import MongoClient
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

base_list = []

categories = ['news', 'focus', 'world-news', 'lead-stories', 'business']
pages = [80, 3, 25, 28, 15]

# categories = ['commentary']
# pages = [15]
hdr = {'User-Agent': 'Mozilla/5.0'} #header settings

source = 'jamaica-gleaner.com'


direct_URLs = []
for c, p in zip(categories, pages):
    for i in range(p):
        url = 'https://jamaica-gleaner.com/sections/' + c + '?page=' + str(i)

        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = requests.get(url, headers = hdr)
        soup = BeautifulSoup(req.content)
        item = soup.find_all('div', {'class' : 'field-item even'})
        for i in item:
            try:
                direct_URLs.append(i.find('a', {'href' : True})['href'])
            except:
                pass
        print('Now scraped ', len(direct_URLs), ' articles from previous page.')
   


direct_URLs = list(set(direct_URLs))
final_result = ['https://jamaica-gleaner.com' + i for i in direct_URLs if 'https://jamaica-gleaner.com' not in i]
print('Total number of urls found: ', len(final_result))

url_count = 0
processed_url_count = 0
for url in final_result:
    if url:
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
            article['source_domain'] = source
            print("newsplease date: ", article['date_publish'])
            print("newsplease title: ", article['title'])
            print("newsplease maintext: ", article['maintext'][:50])


            ## Fixing Date:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get Date
            try:
                date = soup.find('meta', property = 'article:published_time')['content']
                article['date_publish'] = dateparser.parse(date).replace(tzinfo=None)
            except:
                try:
                    date = soup.find('span', {'class' : "jg-published-created"}).text
                    article['date_publish'] = dateparser.parse(date)
                except:
                    pass
            if article['date_publish']:
                print('Date modified: ', article['date_publish'])   
            
          
           

            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                if c == "commentary":
                    colname = f'opinion-articles-{year}-{month}'
                    article['primary_location'] = "JAM"
                else:
                    colname = f'articles-{year}-{month}'
                #print(article)
            except:
                colname = 'articles-nodate'
            #print("Collection: ", colname)
            try:
                #TEMP: deleting the stuff i included with the wrong domain:
                #myquery = { "url": final_url, "source_domain" : 'web.archive.org'}
                #db[colname].delete_one(myquery)
                # Inserting article into the db:
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
