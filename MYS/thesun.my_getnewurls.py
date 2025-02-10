# Packages:

from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from pymongo import MongoClient
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import re

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p


hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

source = 'thesun.my'



base = 'https://thesun.my/search-result/-/search/the/false/true/20240901/20241203/relevance/false/false/0/0/meta/0/0/0/'
hdr = {'User-Agent': 'Mozilla/5.0'}
len_final_result = 0
url_count = 0
processed_url_count = 0


for p in range(1, 1045+1):
    direct_URLs = []

    link = base + str(p) 
    req = requests.get(link, headers = hdr)
    soup = BeautifulSoup(req.content)
    print(link)
    item = soup.find_all('div', {'class' : 'headline'})
    for i in item:
        # if "/opinion" in i:
        direct_URLs.append(i.find('a')['href'])
    direct_URLs = list(set(direct_URLs))
    print('Now scraped ', len(direct_URLs), ' articles from previous page.')

            
    direct_URLs = list(set(direct_URLs))
    direct_URLs = ['https://thesun.my' + i for i in direct_URLs]

    blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
    blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
    direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

    final_result = direct_URLs.copy()
    len_final_result += len(final_result)
    print('Total number of urls found: ', len_final_result)


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
                article['url'] = url
                print("newsplease title: ", article['title'])

                if not article['maintext']:
                    try:
                        maintext = soup.find('div', {'class' : 'paragraph'}).text
                        article['maintext'] = maintext.strip()
                    except:
                        article['maintext'] =  article['maintext'] 

                print("newsplease maintext: ", article['maintext'][:50])


                ## Fixing Date:
                soup = BeautifulSoup(response.content, 'html.parser')
                try:
                    date = soup.find('li', {'class' : 'date'}).text
                    article['date_publish'] = dateparser.parse(date, settings = {'DATE_ORDER' : 'DMY'})
                except:
                    article['date_publish'] = article['date_publish']
                print("newsplease date: ", article['date_publish'])

                
                try:
                    year = article['date_publish'].year
                    month = article['date_publish'].month
                    if "/opinion" in url:
                        colname = f'opinion-articles-{year}-{month}'
                        article['primary_location'] = "MYS"
                    else:
                        colname = f'articles-{year}-{month}'
                    #print(article)
                except:
                    colname = 'articles-nodate'
                # print("Collection: ", colname)
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
            print('\n',processed_url_count, '/', len_final_result, 'articles have been processed ...\n')

        else:
            pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
