# Packages:
from typing import final
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import dateparser
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease

text = """http://www.lesoftonline.net/articles/des-candidats-malheureux-paient-des-avocats
http://www.lesoftonline.net/articles/lhomme-de-lannée
http://www.lesoftonline.net/articles/ne-laissons-pas-des-théâtreux-faire-la-politique
http://www.lesoftonline.net/articles/le-complot-d’effacement-de-masimanimba-déjoué
http://www.lesoftonline.net/articles/parler-moins-agir-plus
http://www.lesoftonline.net/articles/nangaa-un-énième-congolais-de-service
http://www.lesoftonline.net/articles/denis-kadima-vante-son-approche
http://www.lesoftonline.net/articles/les-nominations-dans-les-états-majors-des-forces-armées-la-réponse-attendue
http://www.lesoftonline.net/articles/à-goma-tuungana-lance-un-appel-de-solidarité-pour-les-enfants-déplacés-de-guerre
http://www.lesoftonline.net/articles/trump-back
http://www.lesoftonline.net/articles/urgence-extrême
http://www.lesoftonline.net/articles/augustin-matata-ponyo-fait-rebondir-bukanga-lonzo
http://www.lesoftonline.net/articles/le-chef-de-letat-met-la-pression-sur-le-gouvernement-en-activant-lévaluation
http://www.lesoftonline.net/articles/chiffré-à-18-milliards-de-us-le-projet-de-budget-suminwa-2025-fait-rêver
http://www.lesoftonline.net/articles/lancien-ministre-rubota-devant-ses-juges
http://www.lesoftonline.net/articles/cessez-le-feu-à-lest-le-rwanda-ny-croirait-pas
http://www.lesoftonline.net/articles/une-autoroute-électrique-dafrique-de-lest-relie-lethiopie-à-son-voisin-kenyan
http://www.lesoftonline.net/articles/bangboka-fait-espérer-kisangani
http://www.lesoftonline.net/articles/jean-pierre-bemba-croit-à-leffet-de-laéroport-de-kisangani
http://www.lesoftonline.net/articles/le-long-chemin-parcouru-par-laéroport-bangboka
http://www.lesoftonline.net/articles/augustin-kabuya-au-cœur-du-débat-sur-la-constitution
http://www.lesoftonline.net/articles/jean-lucien-bussa-veut-donner-une-impulsion-aux-entreprises-publiques
http://www.lesoftonline.net/articles/léconomie-congolaise-en-position-satisfaisante
http://www.lesoftonline.net/articles/accusé-dappel-à-la-désobéissance
http://www.lesoftonline.net/articles/alingete-couronné
http://www.lesoftonline.net/articles/cet-acte-de-reconnaissance-publique
http://www.lesoftonline.net/articles/une-victoire-diplomatique-le-congo-est-élu-membre-du-conseil-des-droits-de-lhomme
http://www.lesoftonline.net/articles/le-procureur-général-près-la-cour-de-cassation-alerte-sur-la-montée-de-la-violence-dans-la
http://www.lesoftonline.net/articles/la-nouvelle-aérogare-de-kisangani-en-voie-douvrir-ses-portes-aux-passagers
http://www.lesoftonline.net/articles/alingete-un-homme-en-danger
http://www.lesoftonline.net/articles/les-congolais-outrés-appellent-au-départ-de-la-francophonie-de-leur-pays
http://www.lesoftonline.net/articles/des-responsables-du-énième-naufrage-dun-navire-sanctionnés
http://www.lesoftonline.net/articles/quatre-dossiers-économiques-traités-en-conseil-des-ministres
http://www.lesoftonline.net/articles/le-congo-engage-la-lutte-contre-le-mpox
http://www.lesoftonline.net/articles/tshisekedi-réitère-son-appel-aux-nations-à-prendre-des-sanctions-contre-le-régime-de-kagame
http://www.lesoftonline.net/articles/à-lest-malgré-la-guerre-se-construit-lavenir
http://www.lesoftonline.net/articles/fayulu-et-ses-ex
http://www.lesoftonline.net/articles/quand-bunia-se-met-sur-la-voie-de-goma-au-plan-des-infrastructures
http://www.lesoftonline.net/articles/en-ituri-un-homme-écoute-son-corps-ose-se-lancer-sans-tout-savoir
http://www.lesoftonline.net/articles/dans-six-mois-la-rva-sa-sort-des-terres-une-polyclinique-moderne-à-ndolo
http://www.lesoftonline.net/articles/léconomie-nationale-annoncée-par-la-bcc-sur-le-sentier-dune-croissance-soutenue
http://www.lesoftonline.net/articles/comment-être-considéré-comme-politiquement-compétent
http://www.lesoftonline.net/articles/fayulu-dialogue-seth-reprend-la-main
http://www.lesoftonline.net/articles/au-foca-2024-xi-jinping-vante-une-communauté-davenir-partagé-chine-afrique
http://www.lesoftonline.net/articles/après-le-carnage-à-makala-la-crise-saccentue-entre-les-magistrats-et-le-ministère-de-la
http://www.lesoftonline.net/articles/crise-bahati-menace-de-quitter-lunion-sacrée
http://www.lesoftonline.net/articles/en-savoir-plus-sur-la-maladie-mpox
"""
direct_URLs = text.split('\n')
direct_URLs = [i for i in direct_URLs if "http" in i]
source = 'lesoftonline.net'

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

# category = ['taxonomy/term/1', 'categories-top/monde', 'categories-top/congo', 'taxonomy/term/9', 'categories-top/economie']
# end_page = [7, 1, 8, 8, 5]
# for c, p_e in zip(category, end_page):
#     for p in range(p_e+1):
#         base_link = 'http://lesoftonline.net/'+c+'?page=' + str(p)
#         hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
#         req = requests.get(base_link, headers = hdr)
#         soup = BeautifulSoup(req.content)
#         item = soup.find_all('h2', {'class' : 'info-title'})
#         for j in item:
#             direct_URLs.append(j.find('a')['href'])
#         print('Now scraped ', len(direct_URLs), ' articles from previous pages.')

# direct_URLs = ['http://lesoftonline.net' + i for i in direct_URLs]

final_result = list(set(direct_URLs))
print('Total number of urls found: ', len(final_result))


url_count = 0
processed_url_count = 0

for url in final_result:
    url = url.strip()
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
            print("newsplease maintext: ", article['maintext'][:50])
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # fix title
            try:
                title = soup.find('strong', {'class' : 'post-title'}).text
                article['title'] = title
            except:
                title = soup.find('title').text.split('|')[0]
                article['title'] = title
            print("newsplease title: ", article['title'])
           
            # fix date
            try:
                date = soup.find('span', {'property' : 'dc:date dc:created'})['content']
                article['date_publish'] = dateparser.parse(date).replace(tzinfo=None)
            except:
                article['date_publish'] = article['date_publish'] 
            print("newsplease date: ", article['date_publish'])
            
            try:
                year = article['date_publish'].year
                month = article['date_publish'].month
                colname = f'articles-{year}-{month}'
                
            except:
                colname = 'articles-nodate'
            
            # Inserti ng article into the db:
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
