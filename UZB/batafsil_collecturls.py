# from bs4 import BeautifulSoup
# import requests
# import pandas as pd
# import random
# import os
# import sys
# import re
# from pymongo import MongoClient
# from pymongo.errors import DuplicateKeyError
# from pymongo.errors import CursorNotFound
# import pandas as pd
# from datetime import date, timedelta
# from newsplease import NewsPlease
# from datetime import datetime
# import dateparser
# import time
# sys.setrecursionlimit(10000)

# header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# # db connection
# db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p




# # Custom Parser
# def batafsiluz_story(soup):
#     """
#     Function to pull the information we want from batafsil.uz stories
#     :param soup: BeautifulSoup object, ready to parse
#     """
#     hold_dict = {}
       

#     # Get Date
#     try:
#         contains_date = soup.find("time", {"class":"entry-date published updated"})
#         article_date = dateparser.parse(contains_date.text)
#         hold_dict['date_publish'] = article_date 
#     except:
#         hold_dict['date_publish'] = None


#     # Get Text

#     try:
#         article_text = soup.find("div", {"class":"entry-content"}).text.strip()

#         article_text = article_text.replace('Ўзбекистон, Тошкент – Batafsil.uz.', '').strip()
#         hold_dict['maintext'] = article_text

#     except:
#         hold_dict['maintext'] = None


#     return hold_dict






# urls = []
# source = 'batafsil.uz'


# # function created
# def scrape(site):
       
#     # getting the request from url
#     r = requests.get(site, headers = header)
       
#     # converting the text
#     s = BeautifulSoup(r.text,"html.parser")

#     url_count = 0

#     for i in s.find_all("a", href = True):
          
#         href = i['href']

#         ## INSERTING IN THE DB:


#         if len(href.split('/')) > 4:

#             if href not in urls:
#                 full_url = 'https://batafsil.uz' + href



#                 print('Scraping:', full_url)
                
#                 try:
#                     response = requests.get(full_url, headers=header)

#                 except:

#                     time.sleep(0.5)
#                     try:
#                         response = requests.get(url, headers=headers)
#                     except:
#                         continue

#                 try:
#                     article = NewsPlease.from_html(response.text).__dict__
#                     soup = BeautifulSoup(response.text, 'html.parser')

#                 except:
#                     continue
                    
#                 # add on some extras
#                 article['date_download']=datetime.now()
#                 article['download_via'] = "Direct2" #change
#                 article['source_domain'] = source
#                 article['url'] = full_url 
#                 article['language'] = 'uz'


#                 # insert fixes from the custom parser
#                 article['maintext'] =  batafsiluz_story(soup)['maintext']


#                 article['date_publish'] = batafsiluz_story(soup)['date_publish']


#                 ## Inserting into the db
#                 try:
#                     year = article['date_publish'].year
#                     month = article['date_publish'].month
#                     colname = f'articles-{year}-{month}'
#                     #print(year)
#                 except:
#                     colname = 'articles-nodate'

#                 try:
#                     # Inserting article into the db:
#                     db[colname].insert_one(article)
#                     print(article['title'])
#                     print(article['maintext'][0:50])
#                     print(article['date_publish'])
                    
#                     url_count = url_count + 1
#                     print("Inserted! in ", colname, " - number of urls so far: ", url_count)
#                 except DuplicateKeyError:
#                     print("DUPLICATE! Not inserted.")

#                 urls.append(full_url)

    
#     # randomly select another href
#     new_url = random.choice(urls)
#     scrape(new_url)
#     print("NEW URL STARTING:", new_url)




# #randomly start with some url
# scrape('https://batafsil.uz/cat/obchestvo/oiladagi-z-ravonlik-muammosi-b-yicha-mutakhassis-z-ravonlik-urbonlari-yillar-davomida-ech-b-lmaganda/')

# #url = 'https://larepublica.pe/politica/congreso/2023/04/10/congreso-fiebre-de-creacion-de-nuevas-universidades-publicas-peruanas-ministerio-de-educacion-rosendo-serna-870690'


from bs4 import BeautifulSoup
import requests
import pandas as pd
import random
import os
import sys
sys.setrecursionlimit(10000)

header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


# site = 'https://batafsil.uz/cat/obchestvo/oiladagi-z-ravonlik-muammosi-b-yicha-mutakhassis-z-ravonlik-urbonlari-yillar-davomida-ech-b-lmaganda/'
# r = requests.get(site, headers = header)
# s = BeautifulSoup(r.text,"html.parser")

# print(len(s.find_all("a", href = True)))

# print(s.find_all("a", href = True)[10])

# print(s.find_all("a", href = True)[60]['href'])


# for i in s.find_all("a", href = True):
          
#     print(i['href'])

# lists
urls = []
   
# function created
def scrape(site):
       
    # getting the request from url
    r = requests.get(site, headers = header)
       
    # converting the text
    s = BeautifulSoup(r.text,"html.parser")
       
    for i in s.find_all("a", href = True):
          
        href = i['href']

        if '/cat/' in href:

            if len(href.split('/')) > 4:

                full_url = 'https://batafsil.uz' + href
    
                if full_url not in urls:
                
                    urls.append(full_url) 

                    #print(href)
                    print('NOW URLS', len(urls))
                    print('LAST URL', full_url)

                    if len(urls) % 100 == 0 and len(urls)!= 0:

                        data_prev = '/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/UZB/batafsil_' + str(len(urls)-100) + '.xlsx'
                        print('DELETING PREVIOUS FILE:', data_prev)

                        if len(urls) - 100 != 0:

                            try:
                            
                                os.remove(data_prev)

                            except:
                                pass

                        print('SAVING NEW FILE')

                        url_data = pd.DataFrame()

                        url_data['url'] = urls
                        dataname = '/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/UZB/batafsil_' + str(len(urls)) + '.xlsx'

                        url_data.to_excel(dataname)

                    # calling it self
                    try:
                        print('NEW URL!!')
                        scrape(full_url)

                    except KeyError:
                    # randomly select another href
                        scrape(random.choice(urls))




# # randomly start with some url
scrape('https://batafsil.uz/cat/proisshestviya/toshkentda-uch-nafar-maktab-uvchisi-k-p-avatli-uyning-tomiga-chi-ib-selfi-ilishgan-/')

# #url = 'https://larepublica.pe/politica/congreso/2023/04/10/congreso-fiebre-de-creacion-de-nuevas-universidades-publicas-peruanas-ministerio-de-educacion-rosendo-serna-870690'


