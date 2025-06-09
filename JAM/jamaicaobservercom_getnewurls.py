# Packages:

from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from datetime import datetime
from pymongo.errors import DuplicateKeyError
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
import re

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

base_list = []

source = 'jamaicaobserver.com'

# direct_URLs = []
# sitemap_base = 'https://www.jamaicaobserver.com/post-sitemap'
hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# start = 482
# end = 487
# for i in range(start, end+1):
#     sitemap = sitemap_base + str(i) + '.xml'
#     req = requests.get(sitemap, headers = hdr)
#     soup = BeautifulSoup(req.content)
#     item = soup.find_all('loc')
#     for i in item:
#         direct_URLs.append(i.text)
#     print('Now scraped ', len(direct_URLs), ' articles from previous page.')



# sitemap_base = 'https://www.jamaicaobserver.com/category/news/page/'

# hdr = {'User-Agent': 'Mozilla/5.0'}
# start = 1
# end = 50
# for i in range(start, end+1):
#     sitemap = sitemap_base + str(i) + '/?host=www-jamaicaobserver-com.newsmemory.netl'
#     req = requests.get(sitemap, headers = hdr)
#     soup = BeautifulSoup(req.content)
#     item = soup.find_all('div', {'class' : 'title'})
#     for i in item:
#         direct_URLs.append(i.find('a')['href'])
#     print('Now scraped ', len(direct_URLs), ' articles from previous page.')



 #header settings
sitemap = 'https://www.jamaicaobserver.com/'

# sitemap_list = []

direct_URLs = []
for year in range(2025, 2026):
    year_str = str(year)
    for month in range(1,4):
        
        if month >=10:
            month_str = str(month)
        else:
            month_str = '0' + str(month)
        for p in range(1, 100):

            sitemap_date = sitemap + year_str + '/' + month_str + '/page/' +str(p)
            req = requests.get(sitemap_date, headers = hdr)
            soup = BeautifulSoup(req.content)
            item = soup.find_all('div', {'class' : 'title'})
            for i in item:
                direct_URLs.append(i.find('a')['href'])
    print('Scraping ', year_str, month_str, ' articles ...')
    print('Now scraped ', len(direct_URLs), ' articles from previous page.')


            

direct_URLs = list(set(direct_URLs))

blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]


# final_result = ['https://www.jamaicaobserver.com' + i for i in direct_URLs if 'https://www.jamaicaobserver.com' not in i]

final_result = direct_URLs.copy()

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
#             print("newsplease date: ", article['date_publish'])
#             print("newsplease title: ", article['title'])
#             print("newsplease maintext: ", article['maintext'][:50])


            ## Fixing Date:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Get Title: 
            
            try:
                article_title = soup.find("title").text
                article['title']  = article_title   

            except:
                try:
                    article_title =  soup.find('meta', property="og:title")['content']
                    article['title']  = article_title
                except:
                    article['title'] = article['title']
                
            if article['title']:
                article['title'] = article['title'].replace('- Jamaica Observer', '')
                print('Title modified: ', article['title'])
                
            # Get Main Text:
            try:
                soup.find("div", {'id' : 'story'}).find_all('p')
                maintext = ''
                for i in soup.find("div", {'id' : 'story'}).find_all('p'):
                    maintext += i.text.strip()
                article['maintext'] = maintext
            except: 
                try:
                    maintext = soup.find("div", {'id' : 'story'}).text
                    article['maintext']  = maintext
                except:
                    article['maintext'] = article['maintext'] 
            if article['maintext']:
                print('Maintext modified: ', article['maintext'][:50])
                
            # Get Date
            try:
                article_date = soup.find('div',{'class' : "article-date block"}).text
                article['date_publish'] = dateparser.parse(article_date)
                        
            except:
                try:
                    article_date = soup.find('div', {'class' : "article-pubdate"}).text
                    article['date_publish'] = dateparser.parse(article_date)
                except:
                    try:
                        article_date = soup.find('small').text
                        article['date_publish'] = dateparser.parse(article_date)
                    except:
                        article['date_publish'] = article['date_publish']

            if article['date_publish']:
                print('Date modified: ', article['date_publish'])
                
                

            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
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
                # db[colname].delete_one({'url' : article['url']})
                # db[colname].insert_one(article)
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

