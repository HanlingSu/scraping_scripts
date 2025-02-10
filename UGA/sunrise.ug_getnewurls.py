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
import pandas as pd

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []
source = 'sunrise.ug'
sitemap_base = 'https://sunrise.ug/post-sitemap'

text = """URL	Images	Change Frequency	Priority	Last Updated
https://sunrise.ug/news/202412/western-union-postbank-ugandas-collaborate-to-accelerate-financial-inclusion.html
1
Weekly	
Medium
January 2, 2025
4:25 pm
https://sunrise.ug/business/202412/airtel-renews-partnership-with-k2-telecom.html
1
Weekly	
Medium
December 28, 2024
3:39 pm
https://sunrise.ug/business/202412/energy-ministry-reassures-country-on-fuel-prices-during-festive-season.html
1
Weekly	
Medium
December 25, 2024
2:54 pm
https://sunrise.ug/business/202412/finance-denies-instructing-bou-to-pay-fraudulent-companies.html
2
Weekly	
Medium
December 23, 2024
8:45 am
https://sunrise.ug/news/202412/conservationists-warn-against-parrot-breeding-for-profit.html
3
Weekly	
Medium
December 18, 2024
11:11 am
https://sunrise.ug/news/202203/suspected-homos-caught-in-act.html
1
Weekly	
Medium
December 10, 2024
12:40 pm
https://sunrise.ug/news/202412/opposition-unites-to-urge-international-pressure-against-besigye-arrest.html
3
Weekly	
Medium
December 10, 2024
10:09 am
https://sunrise.ug/news/sports/202412/taekwondo-sport-witnesses-exponential-growth-courtesy-of-koreas-support.html
1
Weekly	
Medium
December 10, 2024
9:45 am
https://sunrise.ug/news/202411/speaker-among-vows-to-unseat-minister-kadaga.html
1
Weekly	
Medium
November 28, 2024
2:59 pm
https://sunrise.ug/business/202411/udbs-green-investment-efforts-receive-praise.html
1
Weekly	
Medium
November 25, 2024
3:25 am
https://sunrise.ug/business/202411/blockchain-will-energise-financial-inclusion.html
2
Weekly	
Medium
November 22, 2024
8:21 am
https://sunrise.ug/news/202411/poultry-sector-players-get-platform-for-sharing-experiences-and-ideas.html
1
Weekly	
Medium
November 21, 2024
4:06 pm
https://sunrise.ug/news-feature/202411/young-innovators-with-climate-smart-ideas-bring-hope-for-poultry-farmers.html
2
Weekly	
Medium
November 21, 2024
3:30 pm
https://sunrise.ug/news/202411/korea-scholarship-beneficiaries-put-smiles-on-the-faces-of-orphans-in-kawanda.html
2
Weekly	
Medium
November 18, 2024
12:42 pm
https://sunrise.ug/business/202411/agriculture-lender-seeks-to-empower-micro-finance-institutions-with-farming-knowledge.html
1
Weekly	
Medium
November 15, 2024
9:16 am
https://sunrise.ug/news/202411/donald-trump-makes-historic-return-to-whitehouse.html
1
Weekly	
Medium
November 11, 2024
7:44 am
https://sunrise.ug/news/202411/csos-want-laws-to-protect-indigenous-seeds.html
1
Weekly	
Medium
November 6, 2024
3:26 pm
https://sunrise.ug/news/202410/206-updf-hang-up-their-guns-return-to-civilian-life.html
1
Weekly	
Medium
October 28, 2024
4:46 pm
https://sunrise.ug/news/202410/ugandas-sports-authorities-pledge-to-promote-taekwondo-in-schools.html
3
Weekly	
Medium
October 26, 2024
3:37 pm
https://sunrise.ug/opinions/guest-writer/202410/nwsc-should-be-empowered-to-manage-waste-in-kla-other-cities.html
2
Weekly	
Medium
October 18, 2024
8:53 pm
https://sunrise.ug/news/202410/mps-from-buganda-bugisu-oppose-disbanding-ucda.html
1
Weekly	
Medium
October 18, 2024
6:03 am
https://sunrise.ug/business/202410/partnership-connects-3000-farmers-in-rwenzori-and-elgon-regions-to-post-bank.html
2
Weekly	
Medium
October 17, 2024
4:59 pm
https://sunrise.ug/opinions/guest-writer/202410/census-blunders-government-should-crack-the-whip-on-professional-negligence.html
1
Weekly	
Medium
October 17, 2024
4:05 pm
https://sunrise.ug/opinions/202410/chicken-a-growing-enterprise-helping-youth-to-become-climate-resilient.html
2
Weekly	
Medium
October 16, 2024
6:02 pm
https://sunrise.ug/news/202410/new-crack-develops-in-kiteezi-garbage-landfill-as-kcca-orders-public-to-vacate-area.html
1
Weekly	
Medium
October 15, 2024
7:33 pm
https://sunrise.ug/news/202410/olivia-lutaaya-18-other-nup-political-prisoners-released-after-guilty-plea.html
1
Weekly	
Medium
October 15, 2024
9:10 am
https://sunrise.ug/news/202410/govt-supports-wash-for-national-development.html
1
Weekly	
Medium
October 12, 2024
10:52 am
https://sunrise.ug/news/202410/time-management-a-cultural-comparison-between-japan-and-uganda.html
2
Weekly	
Medium
October 11, 2024
12:14 pm
https://sunrise.ug/business/202410/korea-supported-smes-showcase-value-addition-at-uganda-international-trade-fair.html
4
Weekly	
Medium
October 9, 2024
2:03 pm
https://sunrise.ug/news/202410/v-p-alupo-honours-korea-with-presence-at-national-day-celebrations.html
1
Weekly	
Medium
October 4, 2024
7:35 am
https://sunrise.ug/news/202409/korea-pledges-to-play-a-more-active-role-in-ugandas-devt.html
1
Weekly	
Medium
October 2, 2024
6:59 pm
https://sunrise.ug/news/202410/post-bank-partners-with-mtnmomo-to-expand-access-to-micro-loans.html
1
Weekly	
Medium
October 2, 2024
10:11 am
https://sunrise.ug/news/202409/onapito-death-grips-teso-media-fraternity.html
1
Weekly	
Medium
September 30, 2024
8:57 am
https://sunrise.ug/news/202409/even-with-karuma-electricity-remains-a-privilege-in-uganda.html
2
Weekly	
Medium
September 29, 2024
4:48 am
https://sunrise.ug/opinions/202409/skills-improvement-needed-for-uganda.html
1
Weekly	
Medium
September 28, 2024
10:11 am
https://sunrise.ug/news/202409/museveni-sacks-kcca-top-bosses-over-kiteezi.html
1
Weekly	
Medium
September 25, 2024
3:03 pm"""
direct_URLs = text.split('\n')
direct_URLs = [i for i in direct_URLs if "https://sunrise.ug/" in i ]
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
            soup = BeautifulSoup(response.content, 'html.parser')
            article = NewsPlease.from_html(response.text, url=url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            # title has no problem


        
            try:
                date = soup.find('time', {'itemprop' : 'datePublished'})['datetime']
                article['date_publish'] = dateparser.parse(date)
            except:
                article['date_publish'] =article['date_publish'] 

            print("newsplease date: ", article['date_publish'])
            print("newsplease title: ", article['title'])
            print("newsplease maintext: ", article['maintext'][:50])
            
            
            # custom parser
            

                        
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                if "/opinions/" in url:
                    colname = f'opinion-articles-{year}-{month}'
                else:
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
