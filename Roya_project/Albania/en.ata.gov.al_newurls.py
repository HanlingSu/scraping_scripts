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

direct_URLs = []
for i in range(9, 26+1):

    sitemap = 'https://en.ata.gov.al/wp-sitemap-posts-post-' +  str(i+1) + '.xml'
    print(sitemap)
    req = requests.get(sitemap, headers = hdr)
    soup = BeautifulSoup(req.content)
    item = soup.find_all('loc')
    print(item.text)
    direct_URLs.append(item.text)


final_result = list(set(direct_URLs))
print(len(final_result))


url_count = 0
processed_url_count = 0

for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            response = requests.get(url, headers=header, verify=False)
            # process
            article = NewsPlease.from_html(response.text, url=url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source


            
            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser')
            
            category = []
            for c in soup.find_all('li', {'class' : 'entry-category'}):
                category.append(c.text)
                
            if category in ['Arts&Culture', '']
            # title has no problem
            print("newsplease title: ", article['title'])
            # Get Main Text:
            try:
                maintext = soup.find('div', {'class': 'field-item even'}).text
                article['maintext'] = maintext.strip()

            except: 
                try:
                    soup.find('div', {'class': 'field-item even'}).find_all('p')
                    maintext = ''
                    for i in soup.find('div', {'class': 'field-item even'}).find_all('p'):
                        maintext += i.text
                    article['maintext'] = maintext.strip()
                except:
                    article['maintext']  = article['maintext'] 
            print("newsplease maintext: ", article['maintext'][:50])
            
            # Get Date
            try:
                date = soup.find('meta', property = 'article:published_time')['content']
                article['date_publish'] = dateparser.parse(date).replace(tzinfo = None)
            except:
                try:
                    date = soup.find('time').text
                    article['date_publish'] = dateparser.parse(date, settings={'DATE_ORDER': 'DMY'})
                except:
                    try:
                        date = soup.find('span', {'class' : 'date'}).text
                        article['date_publish'] = dateparser.parse(date, settings={'DATE_ORDER': 'DMY'})
                    except:
                        date = None
                        article['date_publish'] = date
            print("newsplease date: ", article['date_publish'])
            
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

