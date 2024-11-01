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

text = """URL
https://sunrise.ug/news/202410/v-p-alupo-honours-korea-with-presence-at-national-day-celebrations.html
https://sunrise.ug/news/202409/korea-pledges-to-play-a-more-active-role-in-ugandas-devt.html
https://sunrise.ug/news/202410/post-bank-partners-with-mtnmomo-to-expand-access-to-micro-loans.html
https://sunrise.ug/news/202409/onapito-death-grips-teso-media-fraternity.html
https://sunrise.ug/news/202409/even-with-karuma-electricity-remains-a-privilege-in-uganda.html
https://sunrise.ug/opinions/202409/skills-improvement-needed-for-uganda.html
https://sunrise.ug/news/202409/museveni-sacks-kcca-top-bosses-over-kiteezi.html
https://sunrise.ug/news/education/202409/koicas-innovative-classroom-structures-restore-educational-hopes-in-flood-hit-s-sudan.html
https://sunrise.ug/news/202409/dps-lumu-seeks-to-change-law-on-election-of-lop-but-some-disagree.html
https://sunrise.ug/news/202408/three-ministries-fight-for-mandate-over-promotion-of-swahili-language.html
https://sunrise.ug/news/202408/mindset-shift-on-waste-management-in-favour-of-sorting-value-addition-needed-to-avert-another-kiteezi-tragedy.html
https://sunrise.ug/news/202408/signing-of-cfa-brings-nile-basin-countries-to-brink-of-victory-but-there-are-warnings-on-further-delays.html
https://sunrise.ug/business/202408/udb-creates-over-50000-jobs-in-2023.html
https://sunrise.ug/news/202407/uganda-clears-mou-on-angololo-project.html
https://sunrise.ug/news/202402/rusumo-hydro-power-dam-a-huge-milestone-achievement-in-nile-cooperation.html
https://sunrise.ug/news/202407/ufcc-headquatera-unveiled.html
https://sunrise.ug/news/202407/biden-ends-re-election-campaign-endorses-his-vice-harris.html
https://sunrise.ug/business/202407/post-bank-launches-mobile-digital-banking-platform.html
https://sunrise.ug/news/202407/ex-president-donald-trump-narrowly-survives-assassination.html
https://sunrise.ug/opinions/guest-writer/202407/state-failure-is-at-the-doorstep-of-environmental-degradation-in-uganda.html
https://sunrise.ug/opinions/guest-writer/202407/state-failure-is-at-the-doorstep-of-environmental-degradation-in-uganda-part-ii.html
https://sunrise.ug/news/202406/watoto-church-sets-up-agri-biz-institute-in-northern-uganda-gets-applause-from-local-leaders.html
https://sunrise.ug/news/202406/nema-cautioned-on-selective-application-of-the-law-in-wetland-restoration.html
https://sunrise.ug/business/202406/14th-financial-reporting-awards-to-focus-on-esg-progress.html
https://sunrise.ug/news/education/202406/cso-advises-govt-on-free-education-to-ensure-universal-access.html
https://sunrise.ug/business/202406/airtel-prides-in-transforming-lives-across-africa.html
https://sunrise.ug/news/202406/ssenyonyi-sidelined-by-parliament-commission-but-vows-not-to-give-up.html
https://sunrise.ug/news/202406/uganda-south-sudan-electricity-transmission-project-receives-security-assurances-as-financing-deal-nears.html
https://sunrise.ug/news/202406/38505.html
https://sunrise.ug/news/202406/south-korea-pledges-to-deepen-ties-with-africa.html
https://sunrise.ug/business/202406/support-finance-officers-to-boost-company-growth-ceos-told.html
https://sunrise.ug/news/sports/202406/korea-govt-supports-taekwondo-system-improvement-in-uganda.html
https://sunrise.ug/news/202405/ucc-to-intensify-regulation-of-online-media-content.html
https://sunrise.ug/news/202405/ssekikubos-motion-faces-hurdles-from-fellow-nrm-mps.html
https://sunrise.ug/news/health/202405/mainstream-mental-health-in-all-government-ministries-mpuuga-tells-govt.html
https://sunrise.ug/business/202405/ex-minister-kyambadde-roots-for-vocational-skills-launches-ziwa-hair-academy.html
https://sunrise.ug/editor/202405/bid-notice-soma-foundation-needs-60-head-of-cattle-for-eid-adhuha-2024.html
https://sunrise.ug/news/202405/korean-mindset-education-conference-explores-ways-to-deepen-mindset-education-in-uganda.html
"""
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
