"""
Created on Nov 8 

Modified: zung-ru
"""
import os
import getpass
from dateutil.relativedelta import relativedelta
import pandas as pd
import os
from pathlib import Path
import re
import pandas as pd
import time
from dotenv import load_dotenv
from pymongo import MongoClient
import re
import bs4
from bs4 import BeautifulSoup
from newspaper import Article
from dateparser.search import search_dates
import dateparser
import requests
from urllib.parse import quote_plus

import time
import json
import multiprocessing
from newsplease import NewsPlease
from datetime import datetime
from tqdm import tqdm
from datetime import datetime, timedelta
import pytz

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

def custom_parser(soup):

    """
    Custom parse the content given url and requested content
    Need to Modify: (1)title parser (2)maintext parser (3)date parser
    Return: title, maintext, and date
    Print: scraped content
    """
   
    
    # Title Parser: 
    try:
        for i in soup.find_all('h1'):
            title = i.text 
            #print('title:   ',title)
    except:
        try:
            title = soup.find_all('meta',property='og:title')[0]['content'] 
            #print('title:   ',title)
        except:
            title = None
            print('Custom_parser: Empty title!')
            
           
        

    # Maintext Parser
    try:
        maintext = ''
        for i in soup.find_all('p'):
            maintext+=i.text
        for i in soup.find_all('div', style="text-align: justify; "):
            maintext += i.text
        for i in soup.find_all('div', style="text-align: justify;"):
            maintext += i.text
            
            #print('maintext:   ', maintext[:50])


    except: 
        try: 
            maintext = ''
            for i in soup.find_all('div', style="text-align: justify; "):
                maintext += i.text
            #print('maintext:   ',maintext[:50])
            print('first try')

        except:
            try:
                maintext = ''
                for i in soup.find_all('p'):
                        maintext += i.text
                #print('maintext:   ',maintext[:50])
                print('second try')

            except:
                try:
                    maintext = ''
                    for i in soup.find('div', {'id':'article_content'}).find_all('p'):
                        maintext += i.text
                    #print('maintext:   ',maintext[:50])
                    

                except:
                    try:
                        maintext = ''
                        for i in soup.find_all('div', style="text-align: justify;"):
                            maintext += i.text
                        #print('maintext:   ',maintext[:50])
                        print('third try')

                    except:  
                        try:
                            
                            maintext = ''
                            for i in soup.find('div', {'id':'article-content'}).find_all('div', {'class':'a3s'}):
                                maintext += i.text   
                            #print('maintext:   ',maintext)
                            print('fourth try')
                        except:
                            try:
                                maintext = ''
                                for i in soup.find_all('p'):
                                    maintext += i.text
                                #print('maintext:   ',maintext)
                                print('fifth try')

                            except:
                                maintext = None
                                print('Custom_parser: Empty maintext!') 


    # Date Parser
    try: 
        for i in soup.find_all( 'span', {'class':"news-detail__info__date__item"}):
            date = str(i.text)
        date = dateparser.parse(date).replace(tzinfo = None)
    
         
    except:
        try:
            for i in soup.find_all( 'time'):
                date=i['datetime']
            date = dateparser.parse(date).replace(tzinfo = None)
            
        except:
            try:
                s = soup.find('script',type="application/ld+json").string
                date = re.findall('"datePublished": "(.*)","dateModified"', s)[0]
                date = dateparser.parse(date).replace(tzinfo = None) 
                
            except:
                try:
                    s = soup.find_all( 'div', {'class':"nd-article__info-block"})
                    date = re.findall('"datePublished": "(.*)","dateModified"', s)[0]
                    date = dateparser.parse(date).replace(tzinfo = None) 
                except:
                    try:
                        s = soup.find('script',type="text/javascript").string
                        date = re.findall('"ppublishdate": "(.*)",', s)[0]
                        date = dateparser.parse(date).replace(tzinfo = None) 

                    except:
                        try:
                            s = soup.find('script',type="application/ld+json").string
                            date = re.findall('"datePublished": "(.*)",', s)[0]
                            date = dateparser.parse(date).replace(tzinfo = None) 

                
                        except:
                            date = None 
                
                            print('Custom_parser: Empty date!')

                    

    return title,maintext, date 





def update_db(list_article, list_year, list_month):
    '''
    Update database given title, maintext, date, urls, year, month, src and lan
    
    Need to Modify: No, all being assigned as arguments
    Return: X
    Print: insert or update outcome
    '''
    uri = 'mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true'
    db = MongoClient(uri).ml4p
    for i in range(len(list_article)):
        try:
            try:
                col_year =  str(int(list_year[i]))
                col_month = str(int(list_month[i]))
                colname = f'articles-{col_year}-{col_month}'
            
            except:
                col_year = None
                col_month = None
                colname = 'articles-nodate'
            
            
            
            l = [j for j in db[colname].find(
            {
                'url': list_article[i]['url']
            } )] 
            if l ==[]:
                db[colname].insert_one(
                    list_article[i]
                )   
                print(f'{i+1}/{len(list_article)}: insert success!: {colname} ---- (title){list_article[i]["title"][:40]}****(main){list_article[i]["maintext"][:40]}')
            else:
                # db[colname].update_one(
                #     {'url': list_article[i]['url']},
                #     {
                #         '$set': {
                #             'date_publish': list_article[i]['date_publish'],
                #             'title': list_article[i]['title'],
                #             'maintext': list_article[i]['maintext'],
                #             'year': col_year,
                #             'month': col_month
                #         }
                #     }
                #      )
                print(f'{i+1}/{len(list_article)}: already in, pass!: {colname} ---- (title){list_article[i]["title"][:40]}****(main){list_article[i]["maintext"][:40]}')
                
        except Exception as err:
            print(f'Error !!!! when updating ({err})')

def collect_urls_sitemap(num):  
    '''
    Collect urls given the iterative items in url  
    Need to Modify: (1) url pattern for sitemap
    '''
    urls=[]
    url = num
    print("Extracting from: ", url)
    reqs = requests.get(url, headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    for link in soup.find_all('loc'):
        urls.append(link.text)
    #for link in soup.find_all('a'):
    #    urls.append(link.get('href')) 
    print(len(urls))
    
    return urls


def collect_urls_year_month_day(yy, mm, days): #(keyword[0],keyword[1])
    '''
    Collect urls given the iterative items in url
    Need to Modify: (1) iterable urls pattern (2) ways to collect urls (3) if any, can filter blacklist
    Return: list of urls
    Print: collecting outcome
    '''

    #iterate thru a month (31 days), collect all urls
    for dd in days:
        urls = []
        try:
            #### change url pattern
            page_url = f'https://kp.ua/archive/{yy}/{mm}/{dd}/'
            page_req = requests.get(page_url,headers=headers)
            page_soup = BeautifulSoup(page_req.content, features="lxml")
            for i in page_soup.find_all('a', {'class':'materials__title'}):
                link = 'https://kp.ua' + i['href']
                if '/daily/' in link:
                    continue
                if link in urls:
                    continue
                else:
                    urls.append(link)
            print(f'{yy}/{mm}/{dd} --------------- total urls:{len(urls)}')
        except:
            print(f'ERROR !!! collecting urls ----------- {yy}/{mm}/{dd}')
            pass   

    print(len(urls))
    
    return urls


def collect_urls_keyword(keyword, page):
    '''
    Collect urls given the iterative items in url
    Need to Modify: (1) iterable urls pattern (2) ways to collect urls (3) if any, can filter blacklist
    Return: list of urls
    Print: collecting outcome
    '''
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    
    urls = []
    bl = ['/spor/','/bugun-ne-pisirsem-diyenlere-gunun-menusu', '/burclarin-sans-ve-para-durumu,', '/burclarin-sans-ve-para-durumu', '/galeri/', '/video/', '/sampiy10/', '/yazarlar/', '/img/', '/video-havuzu/', '/arama?q=', '/advertorial/', '/anne-cocuk/', '/amp/']
    try:
        #### change url pattern
        page_url = f'https://www.posta.com.tr/arama/?q=+&type=news&start_date={keyword}&end_date=1{keyword}'
        print(page_url)
        page_req = requests.get(page_url,headers=headers)
        page_soup = BeautifulSoup(page_req.content, features="html.parser")
        for i in page_soup.find_all('a', {'class':"news__link"}):
            link = "https://www.posta.com.tr" + i['href']

            if all(element not in link for element in bl):

                print('link collected: ', link)
                urls.append(link)
        urls = list(set(urls))
        print(f'total urls:{len(urls)}')
        #######
    except:
        print(f'ERROR !!! collecting urls ----------- {page}')
        pass   

    
    return urls         
            
            
    
       
            
def news_please(response, download_via, url):
    
    article = NewsPlease.from_html(response.text, url=url).__dict__
    article['date_download']= datetime.now()
    article['download_via'] = download_via
    
    return article
            

def get_content(urls, _custom_parser, download_via, _title, _maintext, _date):
    
    headers =  {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    list_article = []
    list_year = []
    list_month = []
    
    for j, url in enumerate(urls):
        
        try:
            response = requests.get(url,headers=headers)
            article = news_please(response = response, download_via=download_via, url=url)

            soup = BeautifulSoup(response.content, features="lxml")
            
            if _custom_parser:
                try:
                
                    title, maintext, date_publish = custom_parser(soup=soup)
                    if _title:
                        article['title'] = title  
                    if _maintext:  
                        article['maintext'] = maintext
                    if _date:
                        article['date_publish'] = date_publish

                    

                except:
                    print('Error when custom parsing, please fix it!')
                
            list_article.append(article)
                    
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                list_year.append(year)
                list_month.append(month)
                
            except:
                year = None
                month = None
                list_year.append(year)
                list_month.append(month)
            
        except Exception as err:
            print(err)
            list_article.append(None)
            list_year.append(None)
            list_month.append(None)
            
        try:
            print(f'({j+1}/{len(urls)})fixing content  {year}/{month}:  (title){article["title"][:40]} ----- (main){article["maintext"][:40]}')
        except:
            print(url, 'Error! Check whether article title and maintext exist' )
            
            
    return list_article, list_year, list_month
    
def split_list(list_to_split, batch_size=20):
    length = len(list_to_split)
    wanted_parts= (length//batch_size)+1
    return [ list_to_split[i*length // wanted_parts: (i+1)*length // wanted_parts] 
             for i in range(wanted_parts) ] 
    

def pipeline(sitemap,
            year_month_day,
            keyword,
            _custom_parser,
            _title, _maintext, _date):
    unique_urls = []
    list_article = []
    list_year = []
    list_month = []
    
    
    if sitemap:
        '''
        Unit: each sitemap
        '''        
        # list_total_url = []
        # total_url = f'https://www.posta.com.tr/sitemap/archive-sitemap.xml'
        # total_req = requests.get(total_url,headers=headers)
        # total_soup = BeautifulSoup(total_req.content, features="lxml")
        # for link in total_soup.find_all('loc'):
        #     list_total_url.append(link.text)
        fromdate = "20230601" 

        todate = "20231230"     

        sources = ['posta.com.tr']

        for source in sources:
            url = "https://web.archive.org/cdx/search/cdx?url=" + source + "&matchType=domain&collapse=urlkey&from=" + fromdate + "&to=" + todate + "&output=json"

            urls = requests.get(url).text
            parse_url = json.loads(urls) #parses the JSON from urls.

            print("Working on ", len(parse_url), "urls from Wayback Machine's archive for", source)
            url_list = []
            final_url_list = []
            for i in range(1,len(parse_url)):
                
                if str(parse_url[i][4]) == "301":
                    orig_url = parse_url[i][2]
                    if orig_url == "https://www." + source + "/":
                        # url_list.append(final_url)
                        pass
                    else:
                        if orig_url == "https://" + source + "/":
                            pass
                        else:
                            tstamp = parse_url[i][1]
                            waylink = tstamp+'/'+orig_url
                            ## Compiles final url pattern:
                            final_url = 'https://web.archive.org/web/' + waylink
                            
                            url_list.append(final_url)

            bl = ['/bugun-ne-pisirsem-diyenlere-gunun-menusu', '/burclarin-sans-ve-para-durumu,', '/burclarin-sans-ve-para-durumu', '/galeri/', '/video/', '/sampiy10/', '/yazarlar/', '/img/', '/video-havuzu/', '/arama?q=', '/advertorial/', '/anne-cocuk/', '/amp/','/video.posta.com/','/api/lazy/']

            
            
            for url in url_list:
                if not any(ext in url for ext in bl) and 'www.posta.com.tr' in url:
                    url = url[43:]
                    print(url)
                    
                    final_url_list.append(url)

            urls1 = final_url_list
            batch_size = 20

            if len(urls1) > batch_size:
                batched_lists = split_list(urls1, batch_size = batch_size)
                for index, ll in enumerate(batched_lists):
                    #print('sitemap: ',int(num)-int(begin_num),'/', int(end_num)-int(begin_num))
                    print(index+1, '/',len(batched_lists))
                    # check if unique
                    ll_urls = [url for url in ll if url not in unique_urls]
                    unique_urls += ll_urls
                    
                    #get content and fix it 
                    print(index+1, '/',len(batched_lists))
                    content1 = get_content(urls=ll_urls, _custom_parser = _custom_parser, download_via='',_title=_title, _maintext=_maintext, _date=_date)
                    list_article, list_year, list_month = content1[0], content1[1], content1[2]
                    
                    #update db by each sitemap
                    proc = multiprocessing.Process(target=update_db(list_article = list_article, list_year = list_year, list_month = list_month))
                    proc.start()


            else:
                # check if unique
                urls1 = [url for url in urls1 if url not in unique_urls]
                unique_urls += urls1
                
                #get content and fix it 
                content1 = get_content(urls=urls1, _custom_parser = _custom_parser, download_via='',_title=_title, _maintext=_maintext, _date=_date)
                list_article, list_year, list_month = content1[0], content1[1], content1[2]
                
                #update db by each sitemap
                proc = multiprocessing.Process(target=update_db(list_article = list_article, list_year = list_year, list_month = list_month))
                proc.start()


        # for nn, url in enumerate(final_url_list):
            
        #     #print('sitemap: ',int(num)-int(begin_num),'/', int(end_num)-int(begin_num))
        #     #collect urls
        #     # urls1 = collect_urls_sitemap(num=url)
        #     batch_size = 20
            ### if the progree is interruppted, you can restart from urls1[index * batch_size] 
            ### eg. if len(urls)= 2000, batch_size = 20, so the len(batched_list) =101,
            ### That is, if you stop at 30/101, you can restart at urls1[29*20] = urls1[580:]
            # if len(urls1) > batch_size:
            #     batched_lists = split_list(urls1, batch_size = batch_size)
            #     for index, ll in enumerate(batched_lists):
            #         #print('sitemap: ',int(num)-int(begin_num),'/', int(end_num)-int(begin_num))
            #         print(nn+1000,'-----',url, index+1, '/',len(batched_lists))
            #         # check if unique
            #         ll_urls = [url for url in ll if url not in unique_urls]
            #         unique_urls += ll_urls
                    
            #         #get content and fix it 
            #         print(nn+1000, '-----',url, index+1, '/',len(batched_lists))
            #         content1 = get_content(urls=ll_urls, _custom_parser = _custom_parser, download_via='',_title=_title, _maintext=_maintext, _date=_date)
            #         list_article, list_year, list_month = content1[0], content1[1], content1[2]
                    
            #         #update db by each sitemap
            #         proc = multiprocessing.Process(target=update_db(list_article = list_article, list_year = list_year, list_month = list_month))
            #         proc.start()


            # else:
            #     # check if unique
            #     urls1 = [url for url in urls1 if url not in unique_urls]
            #     unique_urls += urls1
                
            #     #get content and fix it 
            #     content1 = get_content(urls=urls1, _custom_parser = _custom_parser, download_via='',_title=_title, _maintext=_maintext, _date=_date)
            #     list_article, list_year, list_month = content1[0], content1[1], content1[2]
                
            #     #update db by each sitemap
            #     proc = multiprocessing.Process(target=update_db(list_article = list_article, list_year = list_year, list_month = list_month))
            #     proc.start()
        

    
    if year_month_day:
        '''
        Unit: month
        '''
        years = [i for i in range(2012,2021)]
        months = ["%.2d" % i for i in range(12, 13)]
        days = ["%.2d" % i for i in range(1,32)]
        
        for yy in year:
            for mm in months:
                #collect urls
                urls2 = collect_urls_year_month_day(yy=yy, mm=mm, days=days)
                
                   # check if unique
                urls2 = [url for url in urls2 if url not in unique_urls]
                unique_urls += urls2
                
                #get content and fix it 
                content2 = get_content(urls=urls2, _custom_parser = _custom_parser, download_via='',_title=_title, _maintext=_maintext, _date=_date)
                list_article, list_year, list_month = content2[0], content2[1], content2[2]
                
                #update db by month
                proc = multiprocessing.Process(target=update_db(list_article = list_article, list_year = list_year, list_month = list_month))
                proc.start()
                
                
    if keyword:
        
        #keywords = [ ('was',630),('on',650), ('has',700), ('an',650), ('not',920),('were',210), ('not',920), ('all',50), ('have',400)]
        start_date = datetime(2023, 6, 1, tzinfo=pytz.UTC)
        end_date = datetime(2023, 9, 10, tzinfo=pytz.UTC)

        # Generate list of dates
        dates = [start_date + timedelta(days=x) for x in range((end_date-start_date).days + 1)]

        # Convert to Unix timestamp in milliseconds
        timestamps_milliseconds = [(int(date.timestamp() * 1000),1) for date in dates]
        # keywords = [('%2520',12000)]
        keywords = timestamps_milliseconds

        for i, keyword_tuple in enumerate(keywords):
            
            keyword = keyword_tuple[0]
            num_page = int(keyword_tuple[1])
            
            for page in range(0,num_page):
                #collect urls
                print(f'keyword: {dates[i]} -------------------------- {page+1}/{num_page} ')
                urls3 = collect_urls_keyword(keyword=keyword, page=page)
                print()
                
                
                    # check if unique
                # urls3 = [url for url in urls3 if url not in unique_urls]
                # unique_urls += urls3
                print(f'keyword: {dates[i]} -------------------------- {page+1}/{num_page} len: {len(urls3)}')
                
                #get content and fix it 
                content3 = get_content(urls=urls3, _custom_parser = _custom_parser, download_via='',_title=_title, _maintext=_maintext, _date=_date)
                list_article, list_year, list_month = content3[0], content3[1], content3[2]
                print(f'keyword: {dates[i]} -------------------------- {page+1}/{num_page} ')
                #update db by month
                proc = multiprocessing.Process(target=update_db(list_article = list_article, list_year = list_year, list_month = list_month))
                proc.start()
                
def query_data(src, colname):
    uri = 'mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true'
    db = MongoClient(uri).ml4p

    cur = db.colname.find({
        'source_domain':{'$in':src}

    })
    query = [data for data in cur]

    return query

def fix_only_with_custom_parser(collections, start_year, end_year, src, _custom_parser, _title, _maintext, _date):

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    dates = pd.date_range(start=datetime(start_year,1,1), end=datetime(end_year,12,1), freq='m')

    if collections == 'year_month':
        for date in tqdm(dates):

            year = date.year
            month = date.month
            colname = f'articles-{year}-{month}'
            articles = query_data(src=src, colname=colname)

            urls = [article['url'] for article in articles]

            content = get_content(urls=urls, _custom_parser = _custom_parser, download_via='',_title=_title, _maintext=_maintext, _date=_date)
            list_article, list_year, list_month = content[0], content[1], content[2]

            proc = multiprocessing.Process(target=update_db(list_article = list_article, list_year = list_year, list_month = list_month))
            proc.start()

    elif collections == 'nodate':

        articles = query_data(src=src, colname='articles-nodate')
        urls = [article['url'] for article in articles]
        content = get_content(urls=urls, _custom_parser = _custom_parser, download_via='',_title=_title, _maintext=_maintext, _date=_date)
        list_article, list_year, list_month = content[0], content[1], content[2] 

        proc = multiprocessing.Process(target=update_db(list_article = list_article, list_year = list_year, list_month = list_month))
        proc.start()
    else:
        print('No collection type to scrape specified!!!')
            
            
if __name__ == "__main__": 
    
    pipeline(sitemap = False,
            year_month_day = False,
            keyword = True,
            _custom_parser = True,
            _title=False, _maintext=False, _date=True)
            
### things to do everytime:
# choose at least one way: collect by sitemap, year_month_day, or keywords
# modify the fuction wrt the way you chose
# modify custom parser to fix title, maintext, date
# 

    # fix_only_with_custom_parser(collections='year_month', 
    #                             start_year=2012, 
    #                             end_year=2021, 
    #                             src=['posta.com.tr'], 
    #                             _custom_parser=True,#always True
    #                             _title=False, 
    #                             _maintext=False, 
    #                             _date=True)
            