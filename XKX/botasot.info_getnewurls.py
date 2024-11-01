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
import re
# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'botasot.info'

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


base = 'https://www.botasot.info/'


category = [ 'bota', 'lajme', 'kosova', 'shqiperia', 'maqedonia', 'opinione']
page_start = [1, 1, 1, 1, 1, 1]
# bota 745-775, shqiperia 596-630 maqedonia 136-143
page_end = [80,150,20,80,35, 10]
for c, ps, pe in zip(category, page_start, page_end):
    direct_URLs = []

    for p in range(ps, pe+1):
        link = base + c + '/?faqe=' +str(p)
        print(link)
        reqs = requests.get(link, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        for i in soup.find('div', {'class' : 'related-down'}).find_all('a'):
            direct_URLs.append(i['href'])
        print(len(direct_URLs))

    direct_URLs = ['https://www.botasot.info' + i for i in direct_URLs ]
    final_result = direct_URLs.copy()

    print(len(final_result))

    month_dict = {
        'janar': 'January',
    'shkurt':'February',
    'mars': 'March',
    'prill':'April',
    'maj': 'May',
    'qershor' : 'June',
    'korrik' : 'July',
    'gusht' : 'August',
    'shtator' : 'September' ,
    'tetor' : 'October',
    'nëntor' : 'November' ,
    'dhjetor' : 'December'
    }

    processed_url_count = 0
    url_count = 0
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
                article['language'] = 'sq'
                
                print("newsplease title: ", article['title'])

            
                soup = BeautifulSoup(response.content, 'html.parser')
            
                if not  article['maintext']:
                    try:
                        maintext = ''
                        for p in soup.find('div', {'id' : '_unlocked'}).find_all('p'):
                            maintext += p.text
                        article['maintext'] = maintext.strip()
                    except:
                        try:
                            article['maintext'] = soup.find('div', {'id' : '_unlocked'}).text.strip()
                        except:
                            article['maintext'] = article['maintext'] 
                print("newsplease maintext: ", article['maintext'][:50])

                try:
                    date_text = soup.find('div', {'class' : 'img-auth'}).text
                    idx = date_text.find('Në ora:')
                    date_text = date_text[:idx+14].split('Më: ')[-1]
                    month_sq = date_text.strip().split(' ')[1]
                    month_en = month_dict[month_sq]
                    date = date_text.replace('Në ora:', '').replace(month_sq, month_en)
                    article['date_publish'] = dateparser.parse(date)
                except:
                    article['date_publish'] = article['date_publish']

                print('newsplease date: ', article['date_publish'])

                try:
                    year = article['date_publish'].year
                    month = article['date_publish'].month
                    if c == "opinione":
                        colname = f'opinion-articles-{year}-{month}'
                        article['primary_location'] = "XKX"
                    else:
                        colname = f'articles-{year}-{month}'
                    #print(article)
                except:
                    colname = 'articles-nodate'

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
                    else:
                        print("Inserted! in ", colname)
                    db['urls'].insert_one({'url': article['url']})
                except DuplicateKeyError:
                    print("DUPLICATE! Not inserted.")
            except Exception as err: 
                print("ERRORRRR......", err)
                pass
            processed_url_count += 1
            print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')
        else:
            pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
