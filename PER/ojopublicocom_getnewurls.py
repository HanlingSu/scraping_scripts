
from pymongo import MongoClient
from bs4 import BeautifulSoup
import dateparser
import requests
from random import randint, randrange
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo.errors import DuplicateKeyError
from newsplease import NewsPlease
import json

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []

sitemap_base = 'https://ojo-publico.com/sitemap.xml?page='

for i in range(1, 4):
    sitemap = sitemap_base + str(i)
    print(sitemap  )
    hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
     #header settings
    req = requests.get(sitemap, headers = hdr)
    soup = BeautifulSoup(req.content)
    item = soup.find_all('loc')
    for i in item:
        url = i.text
        direct_URLs.append(url)

    print(len(direct_URLs))
direct_URLs = list(set(direct_URLs))
final_result = direct_URLs.copy()[::-1]
# [1766:]
# final_result = ['https://ojo-publico.com/sala-del-poder/el-poder-detras-la-educacion-universitaria-privada',
#  'https://ojo-publico.com/ambiente/mineria-ilegal-peru-avanza-mas-30-distritos-la-amazonia',
#  'https://ojo-publico.com/ambiente/territorio-amazonas/se-duplican-dragas-ilegales-para-la-extraccion-oro-el-cenepa',
#  'https://ojo-publico.com/ambiente/territorio-amazonas/mineria-ilegal-loreto-incremento-dragas-el-rio-nanay',
#  'https://ojo-publico.com/ambiente/territorio-amazonas/crimen-y-violencia-el-foco-la-mineria-ilegal-del-rio-nanay',
#  'https://ojo-publico.com/ambiente/territorio-amazonas/minem-resta-importancia-concesion-sobre-el-rio-nanay',
#  'https://ojo-publico.com/ojolab/instituto-reuters-ojopublico-es-uno-los-medios-mas-leidos-del-peru',
#  'https://ojo-publico.com/politica/cit-peru-la-organizacion-que-impulsa-el-cuestionado-plan-bukele',
#  'https://ojo-publico.com/derechos-humanos/genero/avance-la-coca-ilegal-aumenta-la-violencia-sexual-la-amazonia',
#  'https://ojo-publico.com/politica/las-violaciones-derechos-detras-del-plan-bukele-seguridad',
#  'https://ojo-publico.com/ojolab/ojopublico-looking-journalist-switzerland-or-germany',
#  'https://ojo-publico.com/ojolab/ojopublico-busca-un-periodista-suiza-o-alemania',
#  'https://ojo-publico.com/ojolab/ojopublico-presentara-filme-del-consagrado-cineasta-hector-galvez',
#  'https://ojo-publico.com/ojolab/conversatorio-cobre-minerales-silenciosos-y-transicion-energetica',
#  'https://ojo-publico.com/entrevistas/oliva-municipalidad-lima-hubiera-podido-ahorrar-s500-millones',
#  'https://ojo-publico.com/entrevistas/tuesta-han-aprobado-la-bicameralidad-para-reelegirse-el-2026',
#  'https://ojo-publico.com/entrevistas/cubas-lava-jato-es-la-razon-por-la-que-quieren-controlar-la-fiscalia',
#  'https://ojo-publico.com/entrevistas/no-hay-razon-para-que-agroexportadores-tengan-privilegios-fiscales',
#  'https://ojo-publico.com/entrevistas/exfiscal-sanchez-dice-que-profugo-castillo-alva-fue-testigo-protegido',
#  'https://ojo-publico.com/entrevistas/quiroz-vigilancia-continuo-cuando-carpeta-estaba-cargo-alfaro',
#  'https://ojo-publico.com/entrevistas/boluarte-no-tiene-una-idea-clara-lo-que-significa-gobernar',
#  'https://ojo-publico.com/entrevistas/natalia-sobrevilla-el-problema-del-peru-es-un-problema-desigualdad',
#  'https://ojo-publico.com/ojobionico/explicador-como-se-calcula-cuantas-personas-son-pobres-el-peru',
#  'https://ojo-publico.com/ambiente/ministerios-impulsan-flexibilizacion-evaluaciones-ambientales',
#  'https://ojo-publico.com/politica/congreso-publico-mas-100-leyes-por-insistencia-pesar-alertas',
#  'https://ojo-publico.com/ojolab/libro-quiulacocha-ensayo-visual-sobre-el-impacto-minero-la-salud',
#  'https://ojo-publico.com/ambiente/territorio-amazonas/documental-los-conflictos-detras-la-proteccion-los-mashco-piro',
#  'https://ojo-publico.com/derechos-humanos/inspectoria-pnp-archivo-11-nuevos-casos-relacionados-las-protestas',
#  'https://ojo-publico.com/latinoamerica/violencia-ecuador-dos-alcaldes-zonas-mineras-asesinados-dias',
#  'https://ojo-publico.com/ambiente/territorio-amazonas/saweto-una-decada-lucha-por-justicia-la-selva-mas-peligrosa',
#  'https://ojo-publico.com/opinion/cartas-y-replicas/exministra-ponce-dice-que-no-tiene-aumento-patrimonial-injustificado',
#  'https://ojo-publico.com/ojolab/no-estamos-solos-unete-la-presentacion-del-libro-ojopublico',
#  'https://ojo-publico.com/derechos-humanos/pension-jubilacion-peru-es-apenas-33-del-salario-promedio',
#  'https://ojo-publico.com/politica/32-anos-del-autogolpe-fujimori-las-evidencias-la-corrupcion',
#  'https://ojo-publico.com/derechos-humanos/essalud-dilata-cumplimiento-fallo-judicial-por-muerte-digna',
#  'https://ojo-publico.com/derechos-humanos/el-dificil-camino-para-morir-dignamente-peru',
#  'https://ojo-publico.com/ambiente/territorio-amazonas/perdida-bosques-crece-entre-retrasos-del-minam-y-cifras-paralelas',
#  'https://ojo-publico.com/ojobionico/explicador-la-ley-prohibe-la-presidenta-recibir-regalos',
#  'https://ojo-publico.com/derechos-humanos/genero/sunedu-favorecio-archivamiento-denuncias-por-hostigamiento-sexual',
#  'https://ojo-publico.com/latinoamerica/la-cuna-del-cacao-ecuador-y-peru-como-origen-la-domesticacion',
#  'https://ojo-publico.com/politica/sunedu-archivo-proceso-contra-universidad-fundada-por-congresista',
#  'https://ojo-publico.com/sala-del-poder/glencore-se-declara-culpable-esquema-internacional-sobornos',
#  'https://ojo-publico.com/politica/boluarte-allanamientos-e-investigacion-por-enriquecimiento-ilicito',
#  'https://ojo-publico.com/aliadosas/membresias-ojopublico-el-periodismo-que-importa-necesita-aliadosas',
#  'https://ojo-publico.com/politica/los-polemicos-abogados-la-nueva-jueza-del-caso-cocteles',
#  'https://ojo-publico.com/ambiente/territorio-amazonas/el-enorme-delfin-que-habito-la-proto-amazonia-hace-16-millones-anos']
print(len(final_result))

url_count = 0
processed_url_count = 0
source = 'ojo-publico.com'
for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            header = hdr = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=header)
            # process
            article = NewsPlease.from_html(response.text, url=url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            
            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # title 
            try:
                title = soup.find('h1', {'class': 'article__title no-margin-top'}).text
                article['title'] = title
            except:
                try:
                    #article__title no-margin-top
                    title = soup.find('meta', {'property' : 'og:title'}).text
                except:
                    article['title'] = article['title'] 
            print("newsplease title: ", article['title'])

            
            try:
                maintext = ''
                for i in soup.find('div', {'class' : 'main-div-body-special'}).find_all('p'):
                    maintext += i.text
                article['maintext'] = maintext.strip()
            except:
                article['maintext']  = article['maintext'] 
            print("newsplease maintext: ", article['maintext'][:50])
            
                      
            try:
                date = soup.find('meta', property = 'article:published_time')['content']
                article['date_publish'] = dateparser.parse(date)
            except:
                try:
                    #article__info-text article__info-date d-none d-lg-inline
                    date = soup.find('span', {'class' : 'date'}).text
                    article['date_publish'] = dateparser.parse(date)
                except:
                    try:
                        date = soup.find('p', {'class' : 'author'}).find('span',{'class' : None}).text

                    except:
                        try:
                            date = json.loads(soup.find('script', type = 'application/ld+json').contents[0])['@graph'][0]['datePublished']
                            article['date_publish'] = dateparser.parse(date)
                        except:
                            try:

                                date = soup.find('span', {'class' : 'article__info-text article__info-date d-lg-none'}).text
                                article['date_publish'] = dateparser.parse(date)
                            except:
                                date = soup.find('div', {'class' : 'story__summary'}).text.split(':')[-1]
                                article['date_publish'] = dateparser.parse(date)
                
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
                # db[colname].delete_one( {'url' : url })
                # db[colname].insert_one(article)
                pass
                print("DUPLICATE! Pass.")
                
        except Exception as err: 
            print("ERRORRRR......", err)
            pass
        processed_url_count += 1
        print('\n',processed_url_count, '/', len(final_result), 'articles have been processed ...\n')
    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
