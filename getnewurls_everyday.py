# Packages:
from json.tool import main
from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
import json
from pymongo import MongoClient
from urllib.parse import urlparse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from pymongo.errors import CursorNotFound
# from peacemachine.helpers import urlFilter
from newsplease import NewsPlease
from dotenv import load_dotenv
import re
import time
import cloudscraper


db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
source_count_dict = dict()


# around half month content within a sitemap
def update_citizendigital(database):
    global url_count, source
    # db connection:
    # db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p 
    db = database
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    sitemap = 'https://citizen.digital/sitemap.xml'

    direct_URLs = []

    source = 'citizen.digital'

    reqs = requests.get(sitemap, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    for link in soup.find_all('loc'):
        direct_URLs.append(link.text)

    for i in range(len(direct_URLs)):
        if 'www.citizen.digital/www.citizen.digital' in direct_URLs[i]:
            direct_URLs[i] = direct_URLs[i].replace('/www.citizen.digital', '', 1)

    blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
    blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
    direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]
    direct_URLs = direct_URLs[:100]
    final_result = list(set(direct_URLs))
    print('Total number of urls found: ', len(final_result))

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
                print("newsplease date: ", article['date_publish'])
                print("newsplease title: ", article['title'])
                print("newsplease maintext: ", article['maintext'][:50])

            
                soup = BeautifulSoup(response.content, 'html.parser')



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
                    else:
                        print("Inserted! in ", colname)
                    db['urls'].insert_one({'url': article['url']})
                except DuplicateKeyError:
                    print("DUPLICATE! Not inserted.")
            except Exception as err: 
                print("ERRORRRR......", err)
                pass
        else:
            pass

    print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
    source_count_dict[source] = url_count

# daily sitemap, but monthly sitemap avaliable if connection break
def update_elheraldohn(database):
    global url_count, source
    # db connection:
    # db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
    db = database

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


    sitemap = 'https://www.elheraldo.hn/sitemapforgoogle.xml'

    source = 'elheraldo.hn'

    direct_URLs = []


    reqs = requests.get(sitemap, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    sitemap2 = soup.find('loc').text

    reqs = requests.get(sitemap2, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    for link in soup.find_all('loc'):
        direct_URLs.append(link.text)

    blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
    blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
    direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

    final_result = list(set(direct_URLs))

    print('Total number of urls found: ', len(final_result))

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
                print("newsplease date: ", article['date_publish'])
                print("newsplease title: ", article['title'])
                print("newsplease maintext: ", article['maintext'][:50])

            
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # fix date
                try:
                    date = json.loads(soup.find('script', type='application/ld+json').string, strict=False)['datePublished']
                    article['date_publish'] = dateparser.parse(date).replace(tzinfo = None)
                except:
                    try:
                        date = soup.find('time').text
                        article['date_publish'] = dateparser.parse(date, settings={'DATE_ORDER' : 'DMY'})
                    except:
                        article['date_publish'] = article['date_publish']

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
                    else:
                        print("Inserted! in ", colname)
                    db['urls'].insert_one({'url': article['url']})
                except DuplicateKeyError:
                    print("DUPLICATE! Not inserted.")
            except Exception as err: 
                print("ERRORRRR......", err)
                pass
        else:
            pass

    print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
    source_count_dict[source] = url_count

# monthly sitemap avaliable 
def update_laprensahn(database):
    global url_count, source
    # db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
    db = database
    # headers for scraping
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


    ## COLLECTING URLS
    urls = []
    direct_URLs = []

    ## NEED TO DEFINE SOURCE!
    source = 'laprensa.hn'

    # STEP 0: Get sitemap urls:
    base = 'https://www.laprensa.hn/sitemapforgoogle.xml'
    reqs = requests.get(base, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    url = soup.find('loc').text
    print("Extracting from: ", url)
    reqs = requests.get(url, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    for link in soup.findAll('loc'):
        direct_URLs.append(link.text)
    
    blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
    blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
    direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

    final_result = list(set(direct_URLs))
    print("Number of URLs found today: ", len(final_result))

    url_count = 0
    source = 'laprensa.hn'
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
                    url_count = url_count + 1
                    print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                    db['urls'].insert_one({'url': article['url']})
                except DuplicateKeyError:
                    db[colname].delete_one({'url' : article['url']})
                    db[colname].insert_one(article)
                    print("DUPLICATE! Not inserted.")
            except Exception as err: 
                print("ERRORRRR......", err)
                pass
        else:
            pass

    print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
    source_count_dict[source] = url_count

# paged empty search result, can go back to a long time ago
def update_proceso(database):
    global url_count, source
    # db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
    db = database
    # headers for scraping
    hdr = {'User-Agent': 'Mozilla/5.0'} #header settings


    ## COLLECTING URLS
    base_list = []

    base = 'https://proceso.hn/page/'


    source = 'proceso.hn'

    for i in range(1, 10):
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
                
                if category in ['Nacionales', 'Al Día', 'Termómetro', 'Política', 'Criterios', 'Internacionales', 'Economía', 'Migrantes', \
                    'Salud', 'Metrópoli', 'Caliente','Sin categoría', 'News', 'Proceso Electoral', 'Más noticias', 'Especial Rusia 2018',\
                         'Mundial Rusia 2018', 'Actualidad', 'Portada Elecciones 2021', 'Costa Rica', 'El Salvador', 'Elecciones EEUU', 'Featured',\
                          'Guatemala', 'Honduras', 'Nicaragua', 'Política Nacional'   ] \
                    or category not in ['Eliminatorias Qatar 2022', 'Ciencia y Tecnología', 'Copa américa 2019', 'Copa américa 2021', 'Copa Oro 2019',\
                         'Cultura y Sociedad', 'Deportes', 'Farándula', 'Foto del día', 'Frase del día', 'Infografias', 'Portada Digital']:
                    try:
                        article_date = soup.find('time')['datetime']
                        article['date_publish'] = dateparser.parse(article_date).replace(tzinfo = None)
                    except:
                        article['date_publish'] = article['date_publish']

                    #text
                    try:
                        soup.find_all('p')
                        maintext = ''
                        for i in soup.soup.find_all('p'):
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
        else:
            pass

    print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
    source_count_dict[source] = url_count

# daily sitemaps, but paged empty search result avaliable
def update_theeastafrican(database):
    global url_count, source
    # db connection:
    # db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
    db = database
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

  
    sitemap = 'https://www.theeastafrican.co.ke/sitemap.xml'

    source = 'theeastafrican.co.ke'

    direct_URLs = []


    reqs = requests.get(sitemap, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    for link in soup.find_all('loc'):
        direct_URLs.append(link.text)

    blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
    blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
    direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

    final_result = list(set(direct_URLs))

    print('Total number of urls found: ', len(final_result))

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
                print("newsplease date: ", article['date_publish'])
                print("newsplease title: ", article['title'])
                print("newsplease maintext: ", article['maintext'][:50])

            
                soup = BeautifulSoup(response.content, 'html.parser')



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
                    else:
                        print("Inserted! in ", colname)
                    db['urls'].insert_one({'url': article['url']})
                except DuplicateKeyError:
                    print("DUPLICATE! Not inserted.")
            except Exception as err: 
                print("ERRORRRR......", err)
                pass
        else:
            pass

    print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
    source_count_dict[source] = url_count

# daily sitemaps, month sitemaps avaliable
def update_ultimahora(database):
    global url_count, source
    # db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
    db = database
    direct_URLs = []
    sitemap = 'https://www.ultimahora.com/sitemap-latest.xml'
    source = 'ultimahora.com'
    hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
    req = requests.get(sitemap, headers = hdr)
    soup = BeautifulSoup(req.content)
    item = soup.find_all('loc')
    for i in item:
        direct_URLs.append(i.text)

    blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
    blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
    direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]


    print(len(direct_URLs))
    final_result = list(set(direct_URLs))
    print(len(final_result))
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
                # title has no problem
                print("newsplease title: ", article['title'])
                print("newsplease maintext: ", article['maintext'][:50])

                
                # custom parser
                soup = BeautifulSoup(response.content, 'html.parser')
                

                    
                # fix date
                try:
                    date = json.loads(soup.find('script', type='application/ld+json').string)[0]['datePublished']
                    article['date_publish'] = dateparser.parse(date).replace(tzinfo= None)
                except:
                    try:
                        date = soup.find('time', {'class' : 'date'}).text
                        article['date_publish'] = dateparser.parse(date)
                    except:
                        article['date_publish'] = article['date_publish']
                
                if  article['date_publish']:
                    print("newsplease date: ",  article['date_publish'])
        
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
        else:
            pass

    print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
    source_count_dict[source] = url_count

# daily sitemap, only contains one day's content
def update_lanacion(database):
    global url_count, source
    # db connection:
    # db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
    db = database
    direct_URLs = []
    sitemap = 'https://www.lanacion.com.py/arcio/sitemap/'
    source = 'lanacion.com.py'
    hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
    req = requests.get(sitemap, headers = hdr)
    soup = BeautifulSoup(req.content)
    item = soup.find_all('loc')
    for i in item:
        direct_URLs.append(i.text)

    blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
    blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
    direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

    print(len(direct_URLs))

    final_result = list(set(direct_URLs))
    print(len(final_result))
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
                # title has no problem
                print("newsplease title: ", article['title'])
                print("newsplease maintext: ", article['maintext'][:50])
                print("newsplease date: ",  article['date_publish'])
                
                # custom parser
                soup = BeautifulSoup(response.content, 'html.parser')
                

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
        else:
            pass

    print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
    source_count_dict[source] = url_count

# daily sitemap, only contains one day content, UGA
def update_nilepost(database):
    global url_count, source
    # db connection:
    # db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
    db = database
    direct_URLs = []
    sitemap = 'https://nilepost.co.ug/sitemap.xml'
    source = 'nilepost.co.ug'

    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'firefox',
            'platform': 'windows',
            'mobile': False
        }
    )

    soup = BeautifulSoup(scraper.get(sitemap).text)
    item = soup.find_all('loc')

    for i in item:
        direct_URLs.append(i.text)


    print(len(direct_URLs))

 
    final_result = direct_URLs.copy()
    print(len(final_result))

    url_count = 0
    processed_url_count = 0

    for url in final_result:
        if url:
            print(url, "FINE")
            ## SCRAPING USING NEWSPLEASE:
            try:
                # process
                soup = BeautifulSoup(scraper.get(url).text)
                article = NewsPlease.from_html(scraper.get(url).text).__dict__
                # add on some extras
                article['url'] = url
                article['date_download']=datetime.now()
                article['download_via'] = "Direct2"
                article['source_domain'] = source
                # title has no problem

                try:
                    category = soup.find('span', {"class" :"mb-md-3 cat"}).text.strip()
                except:
                    category = "News"
                print(category)


                if category in ["Food Hub", "Love Therapist", "Let's Talk About Sex", "Hatmahz Kitchen", "Tour & Travel", "Entertainment", "Homes", "Lifestyle", "Technology", "Ask the Mechanic"\
                                , "Sports", "Place-It", "StarTimes Uganda Premier League", "World Cup", ]:
                    article['date_publish'] = None
                    article['title'] = 'From uninterested category'
                    article['maintext'] = None
                    print( article['title'], category)
                else:
                    try:
                        maintext = ''
                        for i in soup.find('div', {'class' : 'content-inner'}).find_all('p', {'class' : None}):
                            maintext += i.text
                        article['maintext'] = maintext.strip()
                    except:
                        try:
                            maintext = ''
                            for i in soup.find('div', {'class' : 'content-inner'}).find_all('div', {'class' : None}):
                                maintext += i.text
                            article['maintext'] = maintext.strip()
                        except:
                            article['maintext'] =  article['maintext']

                    if "No Excerpt" in article['maintext'][:15]:
                        article['maintext'] = '\n'.join(article['maintext'].split('\n')[1:])

                    if not article['date_publish']:
                        try:
                            date =  json.loads(soup.find_all('script', {'type' : "application/ld+json"})[1].contents[0], strict=False)['datePublished']
                            article['date_publish'] = dateparser.parse(date)
                        except:
                            article['date_publish'] = article['date_publish']

                    print("newsplease date: ", article['date_publish'])
                    print("newsplease title: ", article['title'])
                    print("newsplease maintext: ", article['maintext'][:50])
                    
                
                try:
                    year = article['date_publish'].year
                    month = article['date_publish'].month
                    colname = f'articles-{year}-{month}'
                    
                except:
                    colname = 'articles-nodate'
                    
                # Inserting article into the db:
                try:
                    year = article['date_publish'].year
                    month = article['date_publish'].month
                    colname = f'articles-{year}-{month}'
                    # print(article)
                except:
                    colname = 'articles-nodate'
                print("Collection: ", colname)
                
                try:
                    db[colname].insert_one(article)
                    # count:
                    if colname != 'articles-nodate':
                        url_count = url_count + 1
                        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                    db['urls'].insert_one({'url': article['url']})
                except DuplicateKeyError:
                    db[colname].delete_one({'url' : url})
                    db[colname].insert_one(article)
                    print("DUPLICATE! Updated.")


            except Exception as err: 
                print("ERRORRRR......", err)
                pass
            processed_url_count += 1
            print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n', url_count, 'articles inserted')
            # if processed_url_count % 300 == 0:
            #     time.sleep(500)
    
        else:
            pass

    print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")

    source_count_dict[source] = url_count

# daily sitemap, only contains one day's content
def update_abccompy(database):
    global url_count, source
    # db connection:
    # db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
    db = database

    direct_URLs = []
    sitemap = 'https://www.abc.com.py/arc/outboundfeeds/news-sitemap/?outputType=xml'
    source = 'abc.com.py'
    # mundo, nacionales, noticias-del-dia, espectaculos, ciencia
    hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
    req = requests.get(sitemap, headers = hdr)
    soup = BeautifulSoup(req.content)
    item = soup.find_all('loc')
    for i in item:
        direct_URLs.append(i.text)
 
    blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
    blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
    direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

    print(len(direct_URLs))
    final_result = list(set(direct_URLs))
    print(len(final_result))
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
                # title has no problem
                print("newsplease title: ", article['title'])
                print("newsplease date: ",  article['date_publish'])
                
                
                
                # custom parser
                soup = BeautifulSoup(response.content, 'html.parser')
            
                try:
                    soup.find('div', {'id': 'article-content'}).find_all('p')
                    maintext = ''
                    for i in soup.find('div', {'id': 'article-content'}).find_all('p'):
                        maintext += i.text.strip()
                    article['maintext'] = maintext
                
                except: 
                    try:
                        maintext = soup.find('div', {'class': 'article-intro'}).text
                        article['maintext'] = maintext
                        
                    except:
                        try:
                            maintext = soup.find('span', {'class' : 'caption'}).text
                            article['maintext'] = maintext
                        except:
                            maintext = None
                            article['maintext']  = maintext
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
        else:
            pass

    print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
    source_count_dict[source] = url_count

# ZAF 
# categorical sitemaps, around one week's content, selenium scraping script avaliable
def update_timeslive(database):
    global url_count, source
    # db connection:
    db = database
    source = 'timeslive.co.za'
    direct_URLs = []
    sitemap = ['https://www.timeslive.co.za/sitemap/sunday-times-daily/news/', 'https://www.timeslive.co.za/sitemap/sunday-times-daily/politics/',\
            'https://www.timeslive.co.za/sitemap/sunday-times-daily/world/', 'https://www.timeslive.co.za/sitemap/sunday-times-daily/business/', \
            'https://www.timeslive.co.za/sitemap/times-live/news/', 'https://www.timeslive.co.za/sitemap/times-live/politics/', 'https://www.timeslive.co.za/sitemap/times-live/investigations/']

    for s in sitemap:
        # mundo, nacionales, noticias-del-dia, espectaculos, ciencia
        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
        req = requests.get(s, headers = hdr)
        soup = BeautifulSoup(req.content)
        item = soup.find_all('loc')
        for i in item:
            direct_URLs.append(i.text)

        print(len(direct_URLs))
 
    blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
    blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
    direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

    final_result = list(set(direct_URLs))
    print(len(final_result))

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
                # title has no problem
                print("newsplease title: ", article['title'])
                if article['maintext']:
                    print("newsplease maintext: ", article['maintext'][:50])
                print("newsplease date: ",  article['date_publish'])
                
                # custom parser
                soup = BeautifulSoup(response.content, 'html.parser')

                if not article['date_publish']:
                    try:
                        date = json.loads(soup.find('script', {'type' : 'application/ld+json'}).contents[0])['datePublished']
                        article['date_publish'] = dateparser.parse(date).replace(tzinfo = None)
                    except:
                        try:
                            date = soup.find('div', {'class' : 'article-pub-date'}).text.split('By')[0]
                            article['date_publish'] = dateparser.parse(date)
                        except:
                            article['date_publish'] = None
                print("newsplease date: ",  article['date_publish'])

                if not article['maintext']:
                    try:
                        maintext = soup.find('div', {'class' : 'article-widgets'}).find('div', {'class' : 'text'}).text
                        article['maintext'] = maintext
                    except:
                        maintext = ''
                        for i in soup.find_all('p'):
                            maintext += i.text
                        article['maintext'] = maintext
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
                    # db[colname].delete_one({ "url": url})
                    # db[colname].insert_one(article)
                    # print("DUPLICATE! updated.")
                    pass
                    print("DUPLICATE! Not inserted.")
                    
            except Exception as err: 
                print("ERRORRRR......", err)
                pass
        else:
            pass

    print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
    source_count_dict[source] = url_count

# categorical sitemaps, three months' content
def update_news24com(database):
    global url_count, source
    # db connection:
    # db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
    db = database

    direct_URLs = []
    source = 'news24.com'
    sitemap = ['https://www.news24.com/news24/sitemap.sitemap?id=1', 'https://www.news24.com/witness/sitemap.sitemap?id=1']
    for s in sitemap:
        urls = []
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        reqs = requests.get(s, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        for i in soup.find_all('loc'):
            urls.append(i.text)
        print(len(urls))
        direct_URLs += urls[:200]

    blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
    blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
    direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

    print(len(direct_URLs))
    final_result = list(set(direct_URLs))
    print(len(final_result))


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
                print("newsplease date: ", article['date_publish'])
                print("newsplease title: ", article['title'])
    #             print("newsplease maintext: ", article['maintext'][:50])

            
                soup = BeautifulSoup(response.content, 'html.parser')

                try:
                    maintext = soup.find('div', {'class' : 'article__body NewsArticle'}).text
                    article['maintext'] = maintext.strip()
                except: 
                    try:
                        maintext = soup.find('div', {'class' : 'article__content'}).text
                        article['maintext']  = maintext.strip()
                    except:
                        try:
                            maintext = soup.find('div', {'class' : 'article__body--locked'}).text
                            article['maintext']  = maintext.strip()
                        except:
                            article['maintext']  =  article['maintext']
                print(article['maintext'][:50])
                
                
                
                try:
                    date = soup.find('meta', property = 'article:published_time')['content']
                    article['date_publish'] = dateparser.parse(date).replace(tzinfo=None)

                except:
                    try:
                        date = soup.find('p', {'class' : 'article__date'}).text
                        article['date_publish'] = dateparser.parse(date).replace(tzinfo=None)

                    except:
                        try:
                            date = soup.find('meta', {'name' : 'publisheddate'})['content']
                            article['date_publish'] = dateparser.parse(date)
                        except:
                            try:
                                date = soup.find('meta', {'name' : 'article-pub-date'})['content']
                                article['date_publish'] = dateparser.parse(date)
                            except:
                                try:
                                    date = soup.find('span', {'class' : 'block datestamp'}).text
                                    article['date_publish'] = dateparser.parse(date)
                                except:
                                    date = None 
                                    article['date_publish'] = None

                
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
                    else:
                        print("Inserted! in ", colname)
                    db['urls'].insert_one({'url': article['url']})
                except DuplicateKeyError:
                    print("DUPLICATE! Not inserted.")
            except Exception as err: 
                print("ERRORRRR......", err)
                pass
        else:
            pass

    print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
    source_count_dict[source] = url_count

# sectional sitemaps, selenium scraping script avaliable
def update_sowetanlive(database):
    global url_count, source
    # db connection:
    # db =  MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
    db = database
    source = 'sowetanlive.co.za'
    direct_URLs = []
    sitemap = ['https://www.sowetanlive.co.za/sitemap/sowetan-live/news/', 'https://www.sowetanlive.co.za/sitemap/sebenza-live/',\
            'https://www.sowetanlive.co.za/sitemap/s-mag/', 'https://www.sowetanlive.co.za/sitemap/business/',\
                'https://www.sowetanlive.co.za/sitemap/google-news/sowetan-live/news/', 'https://www.sowetanlive.co.za/sitemap/google-news/sowetan-live/sebenza-live/',\
                    'https://www.sowetanlive.co.za/sitemap/google-news/sowetan-live/s-mag/', 'https://www.sowetanlive.co.za/sitemap/google-news/sowetan-live/business/' ]

    for s in sitemap:
        # mundo, nacionales, noticias-del-dia, espectaculos, ciencia
        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
        req = requests.get(s, headers = hdr)
        soup = BeautifulSoup(req.content)
        item = soup.find_all('loc')
        for i in item:
            direct_URLs.append(i.text)

        print(len(direct_URLs))

    blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
    blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
    direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]


    final_result = list(set(direct_URLs))
    print(len(final_result))


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
                print("newsplease date: ", article['date_publish'])
                print("newsplease title: ", article['title'])
                if article['maintext']:
                    print("newsplease maintext: ", article['maintext'][:50])

                ## Fixing Date:
                soup = BeautifulSoup(response.content, 'html.parser')

                if not article['maintext']:
                    soup.find_all('p')
                    maintext = ''
                    for i in soup.find_all('p'):
                        maintext += i.text
                    article['maintext'] = maintext.strip()
                    print("newsplease maintext: ", article['maintext'][:50])

                

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
                    url_count = url_count + 1
                    print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                    db['urls'].insert_one({'url': article['url']})
                except DuplicateKeyError:
                    myquery = { "url": url, "source_domain" : source}
                    db[colname].delete_one(myquery)
                    db[colname].insert_one(article)

                    print("DUPLICATE! updated.")
            except Exception as err: 
                print("ERRORRRR......", err)
                pass
        else:
            pass

    print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
    source_count_dict[source] = url_count

# daily sitemap, selenium scraping script avaliable
def update_isolezwe(database):
    global url_count, source
    # db connection:
    db = database
    # db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
    source = 'isolezwe.co.za'
    direct_URLs = []

    sitemap = 'https://www.isolezwe.co.za/sitemap-1.xml'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    reqs = requests.get(sitemap, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')


    for i in soup.find_all('loc'):
        direct_URLs.append(i.text)
    print(len(direct_URLs))

    blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
    blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
    direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

    final_result = list(set(direct_URLs))
    print(len(final_result))


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
                print("newsplease date: ", article['date_publish'])
                print("newsplease title: ", article['title'])
    #             print("newsplease maintext: ", article['maintext'][:50])

            
                soup = BeautifulSoup(response.content, 'html.parser')

                try:
                    maintext = soup.find('div', {'class' : 'articleBodyMore'}).text
                    article['maintext'] = maintext.strip()
                except: 
                    try:
                        maintext = soup.find('div', {'class' : 'articleBody'}).text
                        article['maintext']  = maintext.strip()
                    except:
                        article['maintext']  =  article['maintext']
                print(article['maintext'][:50])
                
                
                
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
                    else:
                        print("Inserted! in ", colname)
                    db['urls'].insert_one({'url': article['url']})
                except DuplicateKeyError:
                    print("DUPLICATE! Not inserted.")
            except Exception as err: 
                print("ERRORRRR......", err)
                pass
        else:
            pass

    print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
    source_count_dict[source] = url_count

# GHA
# daily sitemap, three days data avaliable, categorical scraping avaliable
def update_newsghanacomgh(database):
    #!/usr/bin/env python3
    # -*- coding: utf-8 -*-
    """
    Created on feb 2 2022

    @author: hanling

    This script updates newsghana.com.gh -- it must be edited to 
    scrape the most recent articles published by the source.

    It needs to be run everytime we need to update GHA sources. 
    """

    # db connection:
    # db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
    global url_count, source
    db = database
    direct_URLs = []
    source = 'newsghana.com.gh'
    sitemap = 'https://newsghana.com.gh/sitemap-news.xml'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    reqs = requests.get(sitemap, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    for i in soup.find_all('loc'):
        direct_URLs.append(i.text)
    print(len(direct_URLs))

    blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
    blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
    direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

    final_result = list(set(direct_URLs))

    print("Total number of urls found: ", len(final_result))

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
                # title has no problem
                print("newsplease title: ", article['title'])
                print("newsplease maintext: ", article['maintext'][:50])
                print("newsplease date: ",  article['date_publish'])
                
                # custom parser
                soup = BeautifulSoup(response.content, 'html.parser')
                
                try:
                    category = soup.find('meta',  property =  'article:section')['content']
                except:
                    category = 'News'
                
                if category in  ['Sports', 'Entertainment', 'Business', 'Travel', 'Science', 'Rumor Mill',\
                        'Opinion', 'Auto', 'Real Estates', 'BusinessWire', 'Finance', 'Agriculture', 'Investments', \
                            'Stock Market', 'Environmental news', 'Technology', 'Lifestyle', 'Profile']: 
                    article['title'] = 'From uninterested category'
    #                 article['date_publish'] = None
                    article['maintext'] = None
                    print(article['title'], category)
                    
                try:
                    maintext = ''
                    soup.find('div', {'class' : 'td-post-content'}).find_all('p')
                    for i in soup.find('div', {'class' : 'td-post-content'}).find_all('p'):
                        maintext += i.text
                    article['maintext'] = maintext
                except:
                    article['maintext'] = article['maintext']

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
                    print("DUPLICATE! NOT INSERTED")
                    
            except Exception as err: 
                print("ERRORRRR......", err)
                pass
        else:
            pass

    print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
    source_count_dict[source] = url_count

# daily sitemap, two days data avaliavle, categorical scraping avaliable
def update_graphiccomgh(database):
    global url_count, source
    db = database
    # db connection:
    direct_URLs = []
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'firefox',
            'platform': 'windows',
            'mobile': False
        }
    )
    hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    source = 'graphic.com.gh'
    sitemap = 'https://www.graphic.com.gh/component/jmap/sitemap/gnews?format=gnews'

    try: 
        
        soup = BeautifulSoup(scraper.get(sitemap).text)


        item = soup.find_all('loc')
        for i in item:
            direct_URLs.append(i.text)
        print(len(direct_URLs))
    except:
        pass

    blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
    blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
    direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

    final_result = list(set(direct_URLs))

    
    url_count = 0
    processed_url_count = 0
    for url in final_result:
        if url:
            print(url, "FINE")
            ## SCRAPING USING NEWSPLEASE:
            try:
                soup = BeautifulSoup(scraper.get(url).text)
                # process
                article = NewsPlease.from_html(scraper.get(url).text).__dict__
                # add on some extras
                article['date_download']=datetime.now()
                article['download_via'] = "Direct2"
                article['source_domain'] = source
                print("newsplease title: ", article['title'])
   
                ## Fixing Date:

                try:
                    contains_date = soup.find("time")
                    contains_date = contains_date["datetime"]
                    article_date = dateparser.parse(contains_date, date_formats=['%d/%m/%Y'])
                    article['date_publish'] = article_date
                except:
                    article_date = article['date_publish']
                    article['date_publish'] = article_date
                print("newsplease date: ", article['date_publish'])

                if not article['maintext']:
                    try:
                        soup.find('div', {'class' : {'$regex' : 'bd-postcontent-3 bd-tagstyles.*'} }).find_all('p')
                        maintext =  ''
                        for i in soup.find('div', {'class' : {'$regex' : 'bd-postcontent-3 bd-tagstyles.*'} }).find_all('p'):
                            maintext += i.text
                        article['maintext'] = maintext
                    except:
                        try:
                            soup.find_all('p')
                            maintetx = ''
                            for i in soup.find_all('p'):
                                maintext += i.text
                            article['maintext'] = maintext
                        except:
                            article['maintext'] = None


                if  article['maintext']:
                    print("newsplease maintext: ", article['maintext'][:50])
            
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
    source_count_dict[source] = url_count

# GEO
# 2 weeks of content avaliable from sitemaps, categorical news avaliable
def update_ambebige(database):
    global url_count, source
    # db connection:
    # db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
    db = database
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    sitemap = 'https://www.ambebi.ge/sitemaps/articles_latest.xml'

    direct_URLs = []

    source = 'ambebi.ge'
    reqs = requests.get(sitemap, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    for link in soup.find_all('loc'):
        direct_URLs.append(link.text)

    direct_URLs = direct_URLs[:3500]
    blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
    blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
    direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

    print(len(direct_URLs))
    final_result = direct_URLs
    print(len(final_result))

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
                article['language'] = 'ka'
            
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # fix maintext
                try:
                    soup.find('div', {'class' : 'article_content'}).find_all('p')
                    maintext = ''
                    for i in soup.find('div', {'class' : 'article_content'}).find_all('p'):
                        maintext += i.text
                    article['maintext']  = maintext.strip()
                except:
                    try:
                        maintext = soup.find('div', {'class' : 'article_content'}).text.strip()
                        article['maintext']  = maintext
                    except:
                        maintext = None
                        article['maintext']  = maintext
                if  article['maintext']:
                    print("newsplease maintext: ", article['maintext'][:50])
                
                # fix date
                try:
                    date = soup.find('div', {'class': "article_date"}).text
                    article['date_publish'] = dateparser.parse(date, settings={'DATE_ORDER': 'DMY'})
                except:
                    try:
                        date = soup.find('div', {'class': 'maintopnewsdate'}).time['datetime']
                        article['date_publish'] =  dateparser.parse(date)
                    except: 
                        try:
                            date = soup.fin('time').text
                            article['date_publish'] = dateparser.parse(date, settings={'DATE_ORDER': 'DMY'})

                        except:
                            date = None 
                            article['date_publish'] = None
                print("newsplease date: ", article['date_publish'])
                
                # fix title
                try:
                    article_title = soup.find('meta',property = "og:title")['content']
                    article['title']  = article_title   
                except:
                    try:
                        article_title = soup.find('title').text.split('|')[0]
                        article['title']  = article_title  
                    except:
                        try:
                            article_title = soup.find('div', {'class' : "article_title sa"}).text
                            article['title']  = article_title  
                        except:
                            article_title = None
                            article['title']  = None
                print("newsplease title: ", article['title'])

                try:
                    year = article['date_publish'].year
                    month = article['date_publish'].month
                    colname = f'articles-{year}-{month}'
                    #print(article)
                except:
                    colname = 'articles-nodate'
                print("Collection: ", colname)
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
        else:
            pass

    print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
    source_count_dict[source] = url_count

# TZA
# 1 week content avaliable, empty search scraping script avaliable
def update_thecitizencotz(database):
    global url_count, source
    # db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
    db = database
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    sitemap = 'https://www.thecitizen.co.tz/sitemap.xml'

    direct_URLs = []
    source = 'thecitizen.co.tz'
    reqs = requests.get(sitemap, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    for link in soup.find_all('loc'):
        direct_URLs.append(link.text)

    direct_URLs = direct_URLs[:2000]
    blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
    blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
    direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

    print(len(direct_URLs))
    final_result = list(set(direct_URLs))
    print(len(final_result))
    

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
                print("newsplease title: ", article['title'])
                
                ## Fixing Date:
                soup = BeautifulSoup(response.content, 'html.parser')
                try:
                    date = json.loads(soup.find('script', type="application/ld+json").string)['datePublished']
                    article['date_publish'] = dateparser.parse(date).replace(tzinfo = None)
                except:
                    try:
                        date = soup.find('h6').text
                        article['date_publish'] = dateparser.parse(date)
                    except:
                        article['date_publish'] =article['date_publish'] 
                print("newsplease date: ", article['date_publish'])
                    
                try:
                    maintext = soup.find('section', {'class':'body-copy'}).text.split('More by this Author')[1].replace('Advertisement', '').strip()
                    article['maintext'] = maintext
                except:
                    try:
                        article['maintext'] = maintext.find('section', {'class': 'body-copy'}).text.replace('Advertisement', '').strip()
                    except:
                        article['maintext'] = article['maintext'] 
                if article['maintext']:
                    print("newsplease maintext: ", article['maintext'][:50])

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
                    pass
                
            except Exception as err: 
                print("ERRORRRR......", err)
                pass
        else:
            pass

    print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")  
    source_count_dict[source] = url_count  

# COL
#daily sitemap, empty search results avaliable
def update_elcolombiano(database):
    global url_count, source
    db = database
    # db connection:
    # db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
    direct_URLs = []

    source = 'elcolombiano.com'
    sitemap_base = 'https://www.elcolombiano.com/sitemapforgoogle.xml'
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = requests.get(sitemap_base, headers = hdr)
    soup = BeautifulSoup(req.content)
    sitemap = soup.find('loc').text

    try: 
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = requests.get(sitemap, headers = hdr)
        soup = BeautifulSoup(req.content)

        item = soup.find_all('loc')
        for i in item:
            direct_URLs.append(i.text)
        print(len(direct_URLs))
    except:
        pass

    blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
    blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
    direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

    final_result = list(set(direct_URLs))

    
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
    source_count_dict[source] = url_count


# IND
# daily sitemap, 1 day's content
def update_thehinducom(database):
    global url_count, source
    db = database
    hdr = {'User-Agent': 'Mozilla/5.0'}

    source = 'thehindu.com'
    sitemap = 'https://www.thehindu.com/sitemap/googlenews/all/all.xml'

    direct_URLs = []

    req = requests.get(sitemap, headers = hdr)
    soup = BeautifulSoup(req.content)

    for i in soup.find_all('loc'):
        direct_URLs.append(i.text)
    print('Now collected',len(direct_URLs), 'URLs')

    blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
    blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
    direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

    final_result = direct_URLs.copy()
    print('Total articles collected', len(final_result))

    url_count = 0
    processed_url_count = 0

    for url in final_result:
        print(url)
        try:
            req = requests.get(url, headers = hdr)
            soup = BeautifulSoup(req.content)
            # time.sleep(1)
            article = NewsPlease.from_html(req.text, url=url).__dict__
            
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source


            print("newsplease title: ", article['title'])
            # fix date
            try:
                date = soup.find('meta', {'name' : 'publish-date'})['content']
                article['date_publish'] = dateparser.parse(date).replace(tzinfo = None)
            except:
                article['date_publish'] = article['date_publish'] 
            print("newsplease date: ", article['date_publish'])

            # fix maintext
            try:
                maintext = ''
                for i in soup.find('div', {'class' :'articleBody'}).find_all('p'):
                    maintext += i.text
                article['maintext'] = maintext
            except:
                try:
                    maintext = ''
                    for i in soup.find('div', {'itemprop' :'articleBody'}).find_all('p'):
                        maintext += i.text
                    article['maintext'] = maintext
                except:
                    try:
                        article['maintext'] = soup.find('h2').text
                    except:
                        article['maintext'] = article['maintext'] 

            if article['maintext']:
                print("newsplease maintext: ", article['maintext'][:50])

        except:
            print('Connection error, continue with next article...')
            continue

        
        
        
        # add to DB
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
                url_count += 1
                print("Inserted! in ", colname, " - number of urls so far: ", url_count)
            db['urls'].insert_one({'url': article['url']})
        except DuplicateKeyError:
            myquery = { "url": url, "source_domain" : source}
            db[colname].delete_one(myquery)
            db[colname].insert_one(article)
            pass
            print("DUPLICATE! UPDATED!")
            
        processed_url_count +=1    
        print('\n',processed_url_count, '/', len(final_result) , 'articles have been processed ...\n')
        
    print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
    source_count_dict[source] = url_count
     

# daily sitemap available 
def update_deccanheraldcom(database):
    global url_count, source
    db = database
    hdr = {'User-Agent': 'Mozilla/5.0'}

    source = 'deccanherald.com'
    sitemap = 'https://www.deccanherald.com/news_sitemap.xml'

    direct_URLs = []

    req = requests.get(sitemap, headers = hdr)
    soup = BeautifulSoup(req.content)

    for i in soup.find_all('loc'):
        direct_URLs.append(i.text)
    print('Now collected',len(direct_URLs), 'URLs')


    final_result = direct_URLs.copy()
    print('Total articles collected', len(final_result))

    url_count = 0
    processed_url_count = 0
    inserted_url_count = 0
    for url in final_result:

        print(url)
        try:
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            response = requests.get(url, headers=header)
            article = NewsPlease.from_html(response.text, url=url).__dict__

            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            print("newsplease title: ", article['title'])

            ## Fixing Date:
            soup = BeautifulSoup(response.content, 'html.parser')
            try:
                date = json.loads(soup.find_all('script', {'type':"application/ld+json"})[-1].contents[0])['datePublished']
                article['date_publish'] = dateparser.parse(date).replace(tzinfo=None)
            except:
                article['date_publish'] =article['date_publish'] 
            print("newsplease date: ", article['date_publish'])

            try:
                maintext = ''
                for i in soup.find_all('div', {'class' : 'story-element story-element-text'}):
                    maintext += (i.text)
                article['maintext'] = maintext
            except:
                article['maintext'] = article['maintext'] 
            print("newsplease maintext: ", article['maintext'][:50])

            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2" #change
            article['source_domain'] = source

            ## Inserting into the db
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'articles-{year}-{month}'
                #print(article)
            except:
                colname = 'articles-nodate'

            try:
                # Inserting article into the db:
                db[colname].insert_one(article)
                # count:
                if colname != 'articles-nodate':
                    inserted_url_count = inserted_url_count + 1

                print("Inserted! in ", colname, " - number of urls so far: ", inserted_url_count)
            except DuplicateKeyError:
                print("DUPLICATE! Not inserted.")

            processed_url_count += 1
            print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

        except Exception as err: 
            print("ERRORRRR......", err)
            pass

    print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
    source_count_dict[source] = url_count

 
    
# daily sitemap, 3 days' content  
def update_mediaindonesiacom(database):
    global url_count, source
    db = database
    # db connection:
    # db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
    direct_URLs = []

    source = 'mediaindonesia.com'
    category = ['politik-dan-hukum', 'ekonomi', 'humaniora', 'megapolitan', 'internasional', 'nusantara']
    for c in category:
        
        sitemap = 'https://mediaindonesia.com/' + c + '/sitemap.xml'
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = requests.get(sitemap, headers = hdr)
        soup = BeautifulSoup(req.content)

        try: 
            hdr = {'User-Agent': 'Mozilla/5.0'}
            req = requests.get(sitemap, headers = hdr)
            soup = BeautifulSoup(req.content)

            item = soup.find_all('loc')
            for i in item:
                direct_URLs.append(i.text)
            print(len(direct_URLs))
        except:
            pass

    blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
    blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
    direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

    final_result = list(set(direct_URLs))

    
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
                print("newsplease title: ", article['title'])
                print("newsplease maintext: ", article['maintext'][:50])
    
                ## Fixing Date:
                soup = BeautifulSoup(response.content, 'html.parser')
                if not  article['date_publish']:
                    try:
                        date_text =  soup.find_all('script', {'type' : 'application/ld+json'})[-1].contents[0].replace('\n', '').replace('\t', '')
                        index = soup.find_all('script', {'type' : 'application/ld+json'})[-1].contents[0].replace('\n', '').replace('\t', '').find('"datePublished"')
                        date = date_text[index+18:index+18+19]
                        article['date_publish'] = dateparser.parse(date)
                    except:
                        article['date_publish'] =  article['date_publish'] 
                print("newsplease date: ", article['date_publish'])
            
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
    source_count_dict[source] = url_count

# BLR
def update_nashaniva(database):
    global url_count, source
    db = database
    # db connection:
    # db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
    direct_URLs = []
    source = 'nashaniva.com'
    sitemap = 'https://www.laprensagrafica.com/_static/sitemaps/lpg-18-4.txt'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    
    today = datetime.today()

    # Format the date as 'year-month-day'
    formatted_date = today.strftime('%Y-%m-%d')

    for page in range(1,4):
        page_str = str(page)
        link = 'https://nashaniva.com/?c=shdate&i=' + formatted_date + '&p=' + page_str +'&lang=ru'
        print(link)
        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
        req = requests.get(link, headers = hdr)
        soup = BeautifulSoup(req.content)
        item =  soup.find_all('a', {'class' : 'news-item__link'})
        for i in item:
            direct_URLs.append(i['href'])
    print('Now collected ', len(direct_URLs), 'articles from previous months...')



    final_result = list(set(direct_URLs))
    final_result = ['https://nashaniva.com' + i for i in final_result if 'https://nashaniva.com' not in i]
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
                response = requests.get(url, headers=header)
                # process
                article = NewsPlease.from_html(response.text, url=url).__dict__
                # add on some extras
                article['date_download']=datetime.now()
                article['download_via'] = "Direct2"
                article['source_domain'] = source
                # title has no problem
                print("newsplease title: ", article['title'])
                print("newsplease maintext: ", article['maintext'][:50])
                print("newsplease date: ",  article['date_publish'])
        

            
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
    source_count_dict[source] = url_count


# SLV
# daily sitemap, 1 day's content 
def update_laprensagrafica(database):
    global url_count, source
    db = database
    # db connection:
    # db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@localhost:8080/?authSource=ml4p').ml4p
    direct_URLs = []
    source = 'laprensagrafica.com'
    sitemap = 'https://www.laprensagrafica.com/_static/sitemaps/lpg-18-4.txt'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

   
    req = requests.get(sitemap, headers = headers)
    #file = BeautifulSoup(req.content, 'html.parser')
    file = BeautifulSoup(req.text, 'html.parser')
    soup_string = str(file)
    vectorurls = soup_string.split()
    #print(soup_string, len(soup_string))
    for link in vectorurls:
        direct_URLs.append(link) 

    direct_URLs = direct_URLs[-100:]
    print("URLs so far: ", len(direct_URLs))


    blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
    blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
    direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

    final_result = list(set(direct_URLs))

    
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
                try:
                    #article_title = soup.find("title").text
                    contains_title = soup.find("meta", {"property":"og:title"})
                    article_title = contains_title['content']
                    article['title']  = article_title   

                except:
                    article['title']  = article['title']

                # Get Main Text:
                try:
                    maintext_contains = soup.find("div", {"class":"news-body"}).text
                    article['maintext'] = maintext_contains
                   
                except: 
                    try:
                        maintext_contains = soup.find("div", {"class":"nota"}).text
                        article['maintext'] = maintext_contains
                    except:
                        article['maintext']  = article['maintext'] 


                try:
                    contains_date = soup.findAll("time")[0]
                    contains_date = contains_date["datetime"]
                    contains_date = contains_date.replace("T"," ")
                    contains_date = contains_date.replace("-"," ")
                    vectordate = contains_date.split()
                    # day, month, year:
                    daystr = vectordate[2]
                    monthstr = vectordate[1]
                    yearstr = vectordate[0]
                    article_date = datetime(int(yearstr),int(monthstr),int(daystr))
                    article['date_publish'] = article_date
                except:
                    try:
                        contains_date = soup.find("time", {"class":"news-date"})
                        contains_date = contains_date['datetime']
                        article_date = dateparser.parse(contains_date,date_formats=['%d/%m/%Y'])
                        article['date_publish'] = article_date  
                    except:
                        try:
                            contains_date = soup.find("meta", {"name":"cXenseParse:recs:publishtime"})
                            contains_date = contains_date['content']
                            article_date = dateparser.parse(contains_date,date_formats=['%d/%m/%Y'])
                            article['date_publish'] = article_date  
                        except:
                            article['date_publish'] = article['date_publish']
   
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
    source_count_dict[source] = url_count
# KEN
def update_kbccoke(database):
    global url_count, source
    db = database
    source = 'kbc.co.ke'

    direct_URLs = []
    base = 'https://www.kbc.co.ke/category/news/page/'
    for p in range(1, 4):
        url = base + str(p)
        print(url)
        hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
        req = requests.get(url, headers = hdr)
        soup = BeautifulSoup(req.content)

        for i in soup.find_all('h3', {'class' : 'entry-title td-module-title'}):
            direct_URLs.append(i.find('a')['href'])
        print(len(direct_URLs))


    blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
    blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
    direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

    final_result = direct_URLs.copy()
    print(len(final_result))

    url_count = 0
    processed_url_count = 0

    for url in final_result:
        # if url:
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
            

            response = requests.get(url, headers=header)

            soup = BeautifulSoup(response.content, 'html.parser')

            try:
                category = soup.find('li', {'class' : 'entry-category'}).text
            except:
                category = 'News'
            
            if category in ['Celebrity', 'Entertainment', 'Lifestyle', 'Business', 'Sports', 'Podcasts', 'Technology', 'Markets', 'Athletics']:
                article['date_publish'] = None
                article['maintext'] = None
                article['title'] = 'From uninterested category!'
                print(article['title'], category)
            else:
                print("newsplease date: ", article['date_publish'])
                print("newsplease title: ", article['title'])
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

        # else:
        #     pass

    print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")

    source_count_dict[source] = url_count
# IDN
# daily categorical news, monthly archive avaliable
def update_jawapos(database):

    global url_count, source
    db = database
    # db connection:
    direct_URLs = []
    source = 'jawapos.com'
    category = ['nasional' , 'surabaya-raya', 'haji', 'berita-sekitar-anda', 'pemilihan', 'hankam', 'pendidikan']
    page = [10, 5, 1, 5, 1, 1, 1]
    base = 'https://www.jawapos.com/'
    
    for c, p in zip(category, page):
        
        url = base + c + '?page=' + str(p)
        
        header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        response = requests.get(url, headers=header)
        soup = BeautifulSoup(response.content, 'html.parser')
        for i in soup.find_all('h2', {'class' : 'latest__title'}):
            direct_URLs.append(i.find('a')['href'])
        print(len(direct_URLs))


    blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
    blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
    direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]

    final_result = direct_URLs.copy()
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
                response = requests.get(url, headers=header)
                # process
                article = NewsPlease.from_html(response.text, url=url).__dict__
                # add on some extras
                article['date_download']=datetime.now()
                article['download_via'] = "Direct2"
                article['source_domain'] = source
                article['language'] = 'id'
                print("newsplease date: ", article['date_publish'])
                print("newsplease title: ", article['title'])
                # article['maintext'] = article['maintext'].replace('JawaPos.com', '')
                # article['maintext'] = article['maintext'].split('-', 1)[1]
                # print("newsplease maintext: ", article['maintext'][:50])

                ## Fixing Date:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                if not article['maintext']:
                    try:
                        maintext = soup.find('div', {'itemprop' : 'articleBody'}).text

                    except:
                        try:
                            maintext = soup.find('div', {'class' : 'content-article'}).text

                        except:
                            try:
                                maintext = soup.find('div', {'class' : 'content-article'}).text

                            except:
                                try:
                                    maintext = soup.find('div', {'class' : 'content'}).text

                                except:
                                    try:
                                        maintext = soup.find('div', {'class' : 'single-content'}).text
                        
                                    except:
                                        try:
                                            soup.find('article').find_all('p')
                                            maintext = ''
                                            for i in soup.find('article').find_all('p'):
                                                maintext += i.text
                                            article['maintext'] = maintext.strip().replace('JawaPos.com', '')
                                        except:
                                            try:
                                                item = soup.find('div', {'class' : 'tdb-block-inner td-fix-index'}).find_all('p')
                                                maintext = ''
                                                for i in item:
                                                    maintext += i.text
                                                article['maintext'] =  maintext.strip().replace('JawaPos.com', '')
                                            except:
                                                article['maintext']  = None

                if article['maintext']:   
                    article['maintext'] =  article['maintext'].replace('JawaPos.com', '').strip().replace('-','', 1).strip()
                    article['maintext'] =  article['maintext'].replace('BALI EXPRESS –', '').strip()
                    print("newsplease maintext: ", article['maintext'][:50])

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
                    pass
                
            except Exception as err: 
                print("ERRORRRR......", err)
                pass
            processed_url_count += 1
            print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')

        else:
            pass

    print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
    source_count_dict[source] = url_count

def update_gazetatema(database):

    global url_count, source
    db = database
    # db connection:
    direct_URLs = []
    source = 'gazetatema.net'
        
    categories = ['sociale', 'antena', 'politika', 'ekonomia', 'bota', 'kronika' ]
    
    url_base = 'https://www.gazetatema.net/category/' 

    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'firefox',
            'platform': 'windows',
            'mobile': False
        }
    )


    for c in categories:
        url = url_base + c
        soup = BeautifulSoup(scraper.get(url).text)
        for i in soup.find_all('div', {'class' : 'a-card_content'}):
            direct_URLs.append(i.find('a')['href'])

    blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
    blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
    direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]
    final_result = direct_URLs.copy()

    final_result = ['https://www.gazetatema.net' + i for i in final_result]
    
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
                response = requests.get(url, headers=header)
                # process
                article = NewsPlease.from_html(response.text, url=url).__dict__
                # add on some extras
                article['date_download']=datetime.now()
                article['download_via'] = "Direct2"
                article['source_domain'] = source
                article['language'] = 'sq'
                
                ## Fixing Date:
                soup = BeautifulSoup(scraper.get(url).text, 'html.parser')
                try:
                    title = soup.find('div', {'class' : 'content-title'}).find('h1').text
                    article['title'] = title
                except:
                    title = soup.finf('meta', property = 'og:title')['content']
                    article['title'] = title
                print("newsplease title: ", article['title'])
                
                
                try:
                    date = soup.find('meta', property = 'article:published_time')['content']
                    print(date)
                    if 'CEST' in date:
                        date = date.replace('CEST', ' ')
                    elif 'CET' in date:
                        date = date.replace('CET', ' ')
                    article['date_publish'] = dateparser.parse(date)
                except:
                    date = soup.find('span', {'class' : 'a-time'}).text
                    article['date_publish'] = dateparser.parse(date)
                print("newsplease date: ", article['date_publish'])
                
                try:
                    maintext = ''
                    for i in soup.find('div', {'class' : 'content-narrow'}).find_all('p'):
                        maintext += i.text
                    article['maintext'] = maintext.strip()
                except:
                    maintext = soup.find('div', {'class' : 'content-narrow'}).text
                    article['maintext'] = maintext.strip()
                print("newsplease maintext: ", article['maintext'][:100])
                    
                
                try:
                    year = article['date_publish'].year
                    month = article['date_publish'].month
                    colname = f'articles-{year}-{month}'
                    #print(article)
                except:
                    colname = 'articles-nodate'

                try:
                    db[colname].insert_one(article)
                    # count:
                    if colname !=  'articles-nodate':
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
    source_count_dict[source] = url_count

# international:
def update_lemonde(database):

    global url_count, source
    db = database
    # db connection:
    direct_URLs = []
    source = 'lemonde.fr'

    sitemap = 'https://www.lemonde.fr/sitemap_news.xml' 

    direct_URLs = []
    hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    req = requests.get(sitemap, headers = hdr)
    soup = BeautifulSoup(req.content)

    for i in soup.find_all('loc'):
        direct_URLs.append(i.text)
    print('Now collected',len(direct_URLs), 'URLs')

    blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
    blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
    direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]
    final_result = direct_URLs.copy()

    print('Total articles collected', len(final_result))

    url_count = 0
    processed_url_count = 0
    for url in final_result:
        if url:
            print(url, "FINE")
            ## SCRAPING USING NEWSPLEASE:
            try:
                header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                response = requests.get(url, headers=header)
                # process
                article = NewsPlease.from_html(response.text, url=url).__dict__
                # add on some extras
                article['date_download']=datetime.now()
                article['download_via'] = "Direct2"
                
                print("newsplease date: ", article['date_publish'])
                print("newsplease title: ", article['title'])
                print("newsplease maintext: ", article['maintext'][:50])
                                
                
                try:
                    year = article['date_publish'].year
                    month = article['date_publish'].month
                    colname = f'articles-{year}-{month}'
                    #print(article)
                except:
                    colname = 'articles-nodate'

                try:
                    db[colname].insert_one(article)
                    # count:
                    if colname !=  'articles-nodate':
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
    source_count_dict[source] = url_count 
    
def update_nytimes(database):

    global url_count, source
    db = database
    # db connection:
    direct_URLs = []
    source = 'lemonde.fr'

    sitemap = 'https://www.lemonde.fr/sitemap_news.xml' 

    direct_URLs = []
    hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    req = requests.get(sitemap, headers = hdr)
    soup = BeautifulSoup(req.content)

    for i in soup.find_all('loc'):
        direct_URLs.append(i.text)
    print('Now collected',len(direct_URLs), 'URLs')

    blacklist =  [( i['blacklist_url_patterns']) for i in db.sources.find({'source_domain' : source})][0]
    blacklist = re.compile('|'.join([re.escape(word) for word in blacklist]))
    direct_URLs = [word for word in direct_URLs if not blacklist.search(word)]
    final_result = direct_URLs.copy()

    print('Total articles collected', len(final_result))

    url_count = 0
    processed_url_count = 0
    for url in final_result:
        if url:
            print(url, "FINE")
            ## SCRAPING USING NEWSPLEASE:
            try:
                header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                response = requests.get(url, headers=header)
                # process
                article = NewsPlease.from_html(response.text, url=url).__dict__
                # add on some extras
                article['date_download']=datetime.now()
                article['download_via'] = "Direct2"
                
                print("newsplease date: ", article['date_publish'])
                print("newsplease title: ", article['title'])
                print("newsplease maintext: ", article['maintext'][:50])
                                
                
                try:
                    year = article['date_publish'].year
                    month = article['date_publish'].month
                    colname = f'articles-{year}-{month}'
                    #print(article)
                except:
                    colname = 'articles-nodate'

                try:
                    db[colname].insert_one(article)
                    # count:
                    if colname !=  'articles-nodate':
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
    source_count_dict[source] = url_count 

while True:
    
    update_citizendigital(db)
    update_elheraldohn(db)
    update_laprensahn(db)
    update_proceso(db)
    update_theeastafrican(db)
    update_ultimahora(db)
    update_abccompy(db)
    update_timeslive(db)
    update_news24com(db)
    update_sowetanlive(db)
    update_isolezwe(db)
    update_newsghanacomgh(db)
    update_ambebige(db)
    update_lanacion(db)
    update_thecitizencotz(db)
    update_elcolombiano(db)
    update_graphiccomgh(db)
    update_thehinducom(db)
    update_deccanheraldcom(db)
    update_mediaindonesiacom(db)
    update_laprensagrafica(db)
    update_jawapos(db)
    update_gazetatema(db)
    # update_kbccoke(db)
    update_nilepost(db)
    update_lemonde(db)
    update_nashaniva(db)
    # update_nytimes(db)
    print("\n\n\n")
    print(datetime.now())
    
    for source, count in source_count_dict.items():
        print("Inserted ", str(count), "articles in source", (source))

    time.sleep(86300)