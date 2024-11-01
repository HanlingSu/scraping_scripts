# Packages:
from typing import final
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import dateparser
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease

text = """http://www.lesoftonline.net/articles/alingete-un-homme-en-danger
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
http://www.lesoftonline.net/articles/laéroport-international-de-ndjili-fait-peau-neuve
http://www.lesoftonline.net/articles/le-cycle-électoral-est-clos
http://www.lesoftonline.net/articles/la-paix-à-luanda
http://www.lesoftonline.net/articles/le-député-michel-moto-muhima-plaide-à-la-rva-sa-pour-laérodrome-de-walikale
http://www.lesoftonline.net/articles/grâce-à-des-mesures-drastiques-laéroport-international-de-ndjili-fait-peau-neuve
http://www.lesoftonline.net/articles/entre-synamac-et-constant-mutamba-la-guerre-entre-juges-et-dupond-moretti-en-france
http://www.lesoftonline.net/articles/plus-de-80-de-femmes-ont-échoué-aux-scrutins
http://www.lesoftonline.net/articles/la-variole-du-singe-sempare-du-congo
http://www.lesoftonline.net/articles/refus-de-visa-business-colossal-pour-les-pays-schengen
http://www.lesoftonline.net/articles/cette-sociale-démocratie-dont-se-réclament-nombre-de-partis
http://www.lesoftonline.net/articles/suminwa-monte-ses-ministres-en-puissance
http://www.lesoftonline.net/articles/il-pleut-abondamment-sur-corneille-nangaa-yobeluo
http://www.lesoftonline.net/articles/le-procès-nangaa
http://www.lesoftonline.net/articles/sous-suminwa-les-mandataires-de-létat-sengagent-désormais
http://www.lesoftonline.net/articles/le-dg-de-congo-airways-sa-est-révoqué-pour-incompétence-par-le-conseil-dadministration
http://www.lesoftonline.net/articles/il-tente-de-corrompre-un-ministre-pele-mongo-en-prison
http://www.lesoftonline.net/articles/première-congolaise-cheffe-du-gouvernement-elle-dit-avoir-reçu-le-message-de-ses
http://www.lesoftonline.net/articles/les-premières-actions-suminwa-sont-jugées-positivement-par-les-chefs-dentreprises
http://www.lesoftonline.net/articles/cette-énième-guerre-contre-ligf
http://www.lesoftonline.net/articles/mise-en-place-des-cadres-à-la-rva-sa
http://www.lesoftonline.net/articles/les-banquiers-chez-largentier-national
http://www.lesoftonline.net/articles/des-hommes-politiques-en-contact-avec-des-rebelles-en-ituri
http://www.lesoftonline.net/articles/congo-airways-va-être-dotée-de-trois-airbus-320
http://www.lesoftonline.net/articles/sauvé-par-son-déstin
http://www.lesoftonline.net/articles/la-stratégie-gagnante-de-la-guerre-au-kivu
http://www.lesoftonline.net/articles/kagame-sous-pression-inédite-des-occidentaux
http://www.lesoftonline.net/articles/le-rapport-onusien-qui-accable-kigali
http://www.lesoftonline.net/articles/espoir-ou-désespoir-pour-léconomie-congolaise
http://www.lesoftonline.net/articles/la-belgique-lance-lalerte-trop-de-demandeurs-dasile-venus-du-congo
http://www.lesoftonline.net/articles/actions-de-sauvegarde-de-lintégrité-du-territoire
http://www.lesoftonline.net/articles/2-août-commémoration-du-génocide-congolais
http://www.lesoftonline.net/articles/face-à-la-guerre-que-faire
http://www.lesoftonline.net/articles/dans-son-discours-du-30-juin-le-président-assure-ses-compatriotes
http://www.lesoftonline.net/articles/les-infrastructures-au-cœur-du-dernier-conseil-des-ministres
http://www.lesoftonline.net/articles/la-rva-sa-sur-la-voie-de-relèvement-même-si-les-défis-restent-énormes
http://www.lesoftonline.net/articles/amorcé-en-2018-le-projet-de-construction-dun-nouvel-aéroport-à-ndjili-tarde-à-démarrer
http://www.lesoftonline.net/articles/un-désordre-organisé-à-laéroport-de-ndjili-mêlé-à-une-léthargie-éloquente
http://www.lesoftonline.net/articles/laffaire-du-coup-détat-manqué
http://www.lesoftonline.net/articles/echec-patent-du-congo-dans-lérection-de-médias-professionnels-de-responsabilité
http://www.lesoftonline.net/articles/ligf-soriente-vers-un-nouveau-cap
http://www.lesoftonline.net/articles/la-mort-de-bofassa
http://www.lesoftonline.net/articles/feu-au-dessus-de-goma
http://www.lesoftonline.net/articles/le-chef-de-letat-appelle-le-gouvernement-à-réévaluer-les-mesures-de-stabilisation-du-cdf
http://www.lesoftonline.net/articles/les-mensonges-de-paul-kagame
http://www.lesoftonline.net/articles/une-enquête-qui-désactive-kigali
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
