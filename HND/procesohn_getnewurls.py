from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
from datetime import datetime
from pymongo.errors import DuplicateKeyError
import requests
from newsplease import NewsPlease
from dotenv import load_dotenv
import dateparser
import re

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

base_list = []

base = 'https://proceso.hn/page/'

hdr = {'User-Agent': 'Mozilla/5.0'} #header settings

source = 'proceso.hn'

for i in range(1, 290):
    base_list.append(base + str(i) + '/?s=e')

print('Scrape ', len(base_list), ' page of search result for ', source)


direct_URLs = []
for b in base_list:
    print(b)
    try: 
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = requests.get(b, headers = hdr)
        soup = BeautifulSoup(req.content)
        
        item = soup.find_all('h3', {'class' : 'entry-title td-module-title'})
        for i in item:
            url = i.find('a', href=True)['href']
            if url:
                direct_URLs.append(url)
        print('Now scraped ', len(direct_URLs), ' articles from previous page.')
    except:
        pass

blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]


direct_URLs =list(set(direct_URLs))

final_result = direct_URLs
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
            
            ## Fixing Date:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            try:
                category = soup.find('div', {'class' : 'tdb-category td-fix-index'}).text
            except:
                category = 'News'
            
            if category in  ['Nacionales', 'Al Día', 'Termómetro', 'Política', 'Criterios', 'Internacionales', 'Economía', 'Migrantes', \
                    'Salud', 'Metrópoli', 'Caliente','Sin categoría', 'News', 'Proceso Electoral', 'Más noticias', 'Especial Rusia 2018',\
                         'Mundial Rusia 2018', 'Actualidad', 'Portada Elecciones 2021', 'Costa Rica', 'El Salvador', 'Elecciones EEUU', 'Featured',\
                          'Guatemala', 'Honduras', 'Nicaragua', 'Política Nacional'   ] \
                    or category not in ['Eliminatorias Qatar 2022', 'Ciencia y Tecnología', 'Copa américa 2019', 'Copa américa 2021', 'Copa Oro 2019',\
                         'Cultura y Sociedad', 'Deportes', 'Farándula', 'Foto del día', 'Frase del día', 'Infografias', 'Portada Digital']:
                
                print(category)
                
                try:
                    article_date = soup.find('time')['datetime']
                    article['date_publish'] = dateparser.parse(article_date).replace(tzinfo = None)
                except:
                    article['date_publish'] = article['date_publish']

                #text
                try:
                    soup.find_all('p')
                    maintext = ''
                    for i in soup.find_all('p'):
                        maintext += i.text
                    article['maintext'] = maintext
                except:
                    article['maintext'] = article['maintext']

                #title
                try:
                    article['title'] = soup.find('meta', property = 'og:title')['content']
                except:
                    try:
                        article['title'] = soup.find('h1', {'class':'tdb-title-text'}).text
                    except:
                        article['title'] = article['title']


                if article['title'] is not None:
                    print('Title modified!', article['title'])

                if article['maintext'] is not None:
                    print('Maintext modified!',  article['maintext'][:50])       

                if article['date_publish']:
                    print('Manually collected date is ', article['date_publish'])

            else:
                article['date_publish'] = None
                article['Maintext'] = None
                article['title'] = 'From uninterested category'
                print(article['title'],'\t', category)


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
                print("DUPLICATE! Not inserted.")
            
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
