from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from random import randint, randrange
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import pandas as pd

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p




downloaded_urls = pd.read_excel('/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/PER/larepublica_35500.xlsx')
downloaded_urls2 = pd.read_excel('/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/PER/larepublica2_50100.xlsx')
downloaded_urls3 = pd.read_excel('/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/PER/larepublica3_90000.xlsx')
downloaded_urls4 = pd.read_excel('/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/PER/larepublica4_178000.xlsx')
downloaded_urls5 = pd.read_excel('/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/PER/larepublica5_368700.xlsx')
downloaded_urls6 = pd.read_csv('/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/PER/larepublica5_398200.csv')


urls = pd.concat([downloaded_urls, downloaded_urls2, downloaded_urls3, downloaded_urls4, downloaded_urls5, downloaded_urls6], ignore_index = True)

old_urls = list(set(urls['url']))
print('OLD FILE SIZE', len(urls))


new_urls1 = pd.read_csv('/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/PER/larepublica5_1140300.csv')

new_urls = pd.concat([new_urls1], ignore_index = True)

urls_final = []

for url in new_urls['url']:

    if url in old_urls:
        continue
    urls_final.append(url)
    

print('NEW FILE SIZE:', len(urls_final))

source = 'larepublica.pe'


header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}



# Custom Parser
def larepublica_story(soup):
    """
    Function to pull the information we want from larepublica.pe stories
    :param soup: BeautifulSoup object, ready to parse
    """
    hold_dict = {}
       

    # Get Date
    try:
        contains_date = soup.find("time", {"class":"TitleSection_main__date__L_7Cf"}).text
        fixed_date = contains_date.split('|')[0].strip()
        article_date = dateparser.parse(fixed_date)
        hold_dict['date_publish'] = article_date 
    except:
        hold_dict['date_publish'] = None


    # Get Text

    try:
        article_text = soup.find("div", {"class":"MainContent_main__body__i6gEa"}).text.strip()

    except:
        article_text = None

    try:
        highlight = soup.find('h2', {'class': 'MainContent_mainContent__teaser__mftWU'}).text.strip()
    
    except:
        highlight = None

    try:
        combined_text = highlight + ' ' + article_text
    except:
        combined_text = article_text
    
    hold_dict['maintext'] = combined_text



    # get title

    try:
        title = soup.find('h1', {"class": 'MainContent_main__title__6UiB8'}).text.strip()
        hold_dict['title'] = title

    except:
        hold_dict['title'] = None

    return hold_dict







blacklisted_sections = ['/espectaculos/', '/cultural/', '/deportes/', '/tecnologia/', '/cine-series/', '/horoscopo/', '/autos/', '/videojuegos/']





url_count = 0
processed_url_count = 0

for url in urls_final:

    if any(section in url for section in blacklisted_sections):
        continue
        print('URL is from blacklisted section: SKIPP')

    if url:
        print(url, "FINE")
        ## SCRAPING with custom parser + newsplease
        try:
            response = requests.get(url, headers=header)

            soup = BeautifulSoup(response.content, 'html.parser')

            # process
            article = NewsPlease.from_html(response.text, url=url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source

            # title, maintext, date are from custom parser
            article['maintext'] = larepublica_story(soup)['maintext']
            article['title'] = larepublica_story(soup)['title']
            article['date_publish'] = larepublica_story(soup)['date_publish']

            print("Parsed date: ",  article['date_publish'])
            print("Parsed title: ", article['title'])
            print('Parsed url:', url)

            if article['maintext']:
                print("Parsed maintext: ", article['maintext'][:50])
            
           
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
        print('\n',processed_url_count, '/', len(urls_final), 'articles have been processed ...\n')
    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
