from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from random import randint, randrange
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

source = 'abzas.org'

direct_URLs = []
categories = ['siyaset', 'cemiyyet', 'iqtisadiyyat', 'dunya']
            #politics  society      economy         world
page_start = [1, 1, 1, 1]
# page_end = [1,1,1,1]
page_end =[2,5,1,2]


base = 'https://abzas.org/category/'

for c, ps, pe in zip(categories, page_start, page_end):
    for p in range(ps, pe+1):
        link = base + c +'?page=' + str(p) 
        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
        req = requests.get(link, headers = hdr)
        soup = BeautifulSoup(req.content)
        item = soup.find_all('div', {'class' : 'news_item'})
        for i in item:
            url = i.find('a')['href']
            direct_URLs.append(url)

        print(len(direct_URLs))

direct_URLs = ['https://abzas.org' + i for i in direct_URLs]
final_result =list(set(direct_URLs))
print(len(final_result))

url_count = 0
processed_url_count = 0

for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            header = hdr = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=header)
            # process
            article = NewsPlease.from_html(response.text, url=url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            # title has no problem
            print("newsplease title: ", article['title'])
                      
            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser')
            
            #date
            month_dict = {
                'Yanvar':'January'  ,
                'Fevral':'February',
                'Mart':'March',
                'Aprel':'April',
                'May':'May',
                'İyun':'June',
                'İyul':'July',
                'Avqust':'August',
                'Sentyabr':'September',
                'Oktyabr':'October',
                'Noyabr':'November',
                'Dekabr':'December'
            }

            try: 
                date = soup.find("div", {"class":"news_date mb-3 mt-3"}).text.strip()
                print(date)
                month = date.split(' ')[1]
                print(month)
                month_new = month_dict[month]
                print(month_new)
                date = date.replace(month, month_new)
                article_date = dateparser.parse(date)
                article['date_publish'] = article_date  
            except:
                article['date_publish'] = None
            print("newsplease date: ",  article['date_publish'])


            #maintext
            try:
                maintext = soup.find('div', {'class' : 'post_content'}).text.strip()
                article['maintext'] = maintext
            except:
                try:

                    maintext = ''
                    soup.find('div', {'class' : 'post_content'}).find_all('p')
                    for i in soup.find('div', {'class' : 'post_content'}).find_all('p'):
                        maintext += i.text
                    article['maintext'] = maintext.strip()
                except:
                    article['maintext'] =article['maintext'] 
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
