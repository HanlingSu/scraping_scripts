# Packages:
from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from datetime import datetime
from pymongo.errors import DuplicateKeyError
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease


# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []
base = 'https://assabah.ma/page/'

source = 'assabah.ma'
for i in range(1, 600):
    link = base + str(i) + '?s'
    print('Now scraping: ', link)
    hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
    req = requests.get(link, headers = hdr)
    soup = BeautifulSoup(req.content)
    item = soup.find_all('h2', {'class' : 'post-title'})

    for i in item:
        direct_URLs.append(i.find('a')['href'])

    print('Now scraped ', len(direct_URLs), ' articles from previous pages.')

# for i in range(len(direct_URLs)):
#     if '/' not in  direct_URLs[i]:
#         direct_URLs[i] = 'https://assabah.ma/' + direct_URLs[i]
#     else:
#         direct_URLs[i] = 'https://assabah.ma' + direct_URLs[i]

final_result = list(set(direct_URLs))

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
            

            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser')
        
                
            # fix date
            try:
                date = soup.find('meta', property="article:published_time")['content']
                article['date_publish'] = dateparser.parse(date).replace(tzinfo = None)

            except:
                article['date_publish'] = article['date_publish']
                
            if article['date_publish']:
                print('custom parser date:', article['date_publish'])
                
                
            # Get Title: 
            try:
                article_title = soup.find('title').text.split('|')[0]
                article['title']  = article_title   
            except:
                try:
                    article_title = soup.find('meta', property="og:title")['content'].split('|')[0]
                    article['title']  = article_title   
                except:
                    article['title']  = article['title'] 
                    
            if article['title'] :
                print('cutsom parser title ', article['title'] )
                

            # Get Main Text:
            try:
                maintext = soup.find('meta', {'name' : 'description'})['content']
                article['maintext'] = maintext[:-35]
            except:
                try:
                    maintext = soup.find('div', {'class' : 'entry-content entry clearfix'}).text.split('ألكانتارا”،غربأكمل القراءة » ')[0]   
                    article['maintext'] = maintext
                except: 
                    try:
                        maintext = soup.find('meta',  property = 'og:description')['content']
                        article['maintext']  = None
                    except:
                        try:
                            maintext= soup.find('div', {'class' : 'entry-content entry clearfix'}).text.split('القراءة')[0]
                            article['maintext']  = maintext
                        except:
                            article['maintext']  = article['maintext']
            if article['maintext']:
                print('custom parser maintext', article['maintext'])


      
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
