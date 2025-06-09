
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

# direct_URLs = []

# sitemap_base = 'https://ojo-publico.com/sitemap.xml?page='

# for i in range(1, 4):
#     sitemap = sitemap_base + str(i)
#     print(sitemap  )
#     hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
#      #header settings
#     req = requests.get(sitemap, headers = hdr)
#     soup = BeautifulSoup(req.content)
#     item = soup.find_all('loc')
#     for i in item:
#         url = i.text
#         direct_URLs.append(url)

#     print(len(direct_URLs))
# direct_URLs = list(set(direct_URLs))
# final_result = direct_URLs.copy()[::-1]
text = """https://ojo-publico.com/ojobionico/explicador-si-hubo-crimenes-lesa-humanidad-el-peru
https://ojo-publico.com/aliadosas/ojopublico-conmemora-el-dia-la-libertad-prensa-tiempos-recios
https://ojo-publico.com/la-tienda/esta-democracia-no-es-democracia-nuevo-libro-ojopublico
https://ojo-publico.com/la-tienda/la-tienda-ojopublico-lanza-nuevos-productos-y-kits
https://ojo-publico.com/aliadosas/hazte-aliado-el-periodismo-y-la-creacion-espacios-civicos-peru
https://ojo-publico.com/sala-del-poder/crimen-organizado/cocaina-sin-fronteras-jueces-liberan-investigados-por-trafico
https://ojo-publico.com/ojobionico/explicador-desinformaciones-sobre-el-apagon-la-peninsula-iberica
https://ojo-publico.com/edicion-regional/solo-el-8-los-colegios-publicos-peru-tienen-bibliotecas
https://ojo-publico.com/entrevistas/mesias-guevara-la-situacion-actual-es-mas-dura-que-los-90
https://ojo-publico.com/entrevistas/vergara-este-gobierno-esta-jodiendo-al-peru-manera-decidida
https://ojo-publico.com/5615/un-rio-la-ruta-del-crimen-el-cruce-las-fronteras-amazonicas
https://ojo-publico.com/5616/trafficking-and-illegal-mining-criminal-life-amazon-river
https://ojo-publico.com/5569/territorio-narco-el-70-las-fronteras-amazonicas
https://ojo-publico.com/5607/la-sombra-los-comandos-la-frontera-se-expande-ecuador-y-peru
https://ojo-publico.com/ambiente/distritos-pobres-lima-sufren-mas-el-aumento-las-temperaturas
https://ojo-publico.com/derechos-humanos/psicologos-facilitaron-carnet-policias-que-estuvieron-protestas
https://ojo-publico.com/entrevistas/rafael-vela-no-somos-capaces-enfrentarnos-solos-fernandez-jeri
https://ojo-publico.com/5563/oro-sin-ley-mineria-ilegal-toma-rio-santiago-la-amazonia-peruana
https://ojo-publico.com/politica/mas-700-denuncias-contra-partidos-el-jne-por-afiliacion-indebida
https://ojo-publico.com/opinion/periodistas-23-paises-rechazan-ley-apci-que-afecta-al-periodismo
https://ojo-publico.com/entrevistas/canaquiri-del-estado-no-espero-nada-defensa-la-naturaleza
https://ojo-publico.com/entrevistas/fernando-tuesta-si-hay-elecciones-ajustadas-van-hablar-fraude
https://ojo-publico.com/cultura/granes-america-latina-no-ha-dado-al-mundo-ideas-politicas-viables
https://ojo-publico.com/politica/precandidatos-luna-y-acuna-acumulan-el-99-la-publicidad-digital
https://ojo-publico.com/edicion-regional/arequipa-enfrenta-el-reto-preservar-el-legado-vargas-llosa
https://ojo-publico.com/5597/ley-apci-boluarte-aprueba-arma-legal-contra-medios-como-ojopublico
https://ojo-publico.com/derechos-humanos/salud/medifarma-el-caso-que-expuso-las-grietas-del-sistema-sanitario
https://ojo-publico.com/politica/tercer-expresidente-condenado-15-anos-carcel-por-lavado-humala
https://ojo-publico.com/5586/riqueza-e-inversion-ausente-radiografia-del-canon-petrolero
https://ojo-publico.com/5600/peru-approves-legal-weapon-against-media-such-ojopublico
https://ojo-publico.com/entrevistas/tania-pariona-ni-bukele-ha-planteado-la-pena-muerte
https://ojo-publico.com/5592/privilegios-fiscales-s100-mil-millones-menos-para-obras-y-servicios
https://ojo-publico.com/derechos-humanos/evaluacion-revela-retroceso-aprendizaje-colegios-privados
https://ojo-publico.com/sala-del-poder/mas-del-60-las-grandes-empresas-puno-se-dedican-la-mineria
https://ojo-publico.com/5578/la-quinta-parte-del-petroleo-mundial-esta-la-amazonia
https://ojo-publico.com/entrevistas/vemos-las-organizaciones-criminales-empezando-tomar-el-poder
https://ojo-publico.com/entrevistas/vasquez-el-estado-fallido-se-construye-desde-hace-tiempo-peru
https://ojo-publico.com/5594/telefonica-del-peru-fundo-tres-empresas-y-las-traslado-su-matriz
https://ojo-publico.com/ojobionico/desinformaciones-cara-las-elecciones-presidenciales-2026
https://ojo-publico.com/5581/narco-territory-70-amazonian-borders
https://ojo-publico.com/entrevistas/cateriano-el-fujimorismo-ratifico-su-comportamiento-antidemocratico
https://ojo-publico.com/ojolab/barra-politica-el-avance-del-crimen-organizado-las-fronteras
https://ojo-publico.com/entrevistas/moncada-tener-al-ejercito-las-calles-no-reduce-la-extorsion
https://ojo-publico.com/5580/app-blindo-al-gobierno-el-85-vacancias-y-acciones-control
https://ojo-publico.com/aliadosas/hazte-aliadoa-el-periodismo-independiente-frente-al-abuso-poder
https://ojo-publico.com/652/oro-incautado-la-historia-secreta-del-proveedor-la-mayor-refineria-suiza
https://ojo-publico.com/5565/lawless-gold-illegal-mining-takes-over-santiago-river-peru
https://ojo-publico.com/5568/el-estado-gasta-mas-usd-756-millones-internet-que-no-sirve
https://ojo-publico.com/opinion/cartas-y-replicas/funcionario-del-serfor-amenaza-ojopublico-por-reportaje-sobre-madera
https://ojo-publico.com/institucional/mision-vision-valores
https://ojo-publico.com/5556/millonarios-contratos-el-ministerio-del-interior-y-alta-rotacion
https://ojo-publico.com/node/5535
https://ojo-publico.com/latinoamerica/teuchitlan-el-infierno-convertido-camposanto-mexico
https://ojo-publico.com/politica/las-investigaciones-que-acorralan-la-presidenta-dina-boluarte
https://ojo-publico.com/5550/operacion-peluche-asi-funciona-la-caza-ilegal-y-el-trafico-monos
https://ojo-publico.com/entrevistas/perez-tello-congreso-se-cargo-legislacion-contra-crimen-organizado
https://ojo-publico.com/politica/librerias-independientes-denuncian-amedrentamiento-desde-el-gobierno
https://ojo-publico.com/entrevistas/luis-duran-los-beneficios-tributarios-perforan-la-idea-del-bien-comun
https://ojo-publico.com/5526/four-loko-viola-las-leyes-peruanas-para-promocionar-sus-productos
https://ojo-publico.com/politica/ley-contra-las-ong-pone-peligro-acceso-justicia-los-mas-pobres
https://ojo-publico.com/5541/la-sombra-lopez-aliaga-renovacion-popular-la-beneficencia
https://ojo-publico.com/politica/sip-identifica-fuerte-debilitamiento-la-libertad-prensa-peru
https://ojo-publico.com/5485/derrame-repsol-tres-anos-sin-calcular-los-costos-del-desastre
https://ojo-publico.com/5528/muertes-protestas-radios-revelan-localizacion-agentes-lima
https://ojo-publico.com/5508/precariedad-la-educacion-ninos-estudian-colegios-que-eran-casas
https://ojo-publico.com/entrevistas/ledesma-hay-ignorancia-y-desesperacion-declaraciones-boluarte
https://ojo-publico.com/5527/telefonica-peru-declaro-perdidas-pero-pago-s1153-millones-matriz
https://ojo-publico.com/5515/patrimonio-fuga-congresistas-se-desprenden-sus-bienes
https://ojo-publico.com/edicion-regional/dudas-investigacion-por-las-muertes-el-real-plaza-trujillo
https://ojo-publico.com/ambiente/territorio-amazonas/corto-la-colmena-ashaninka-y-sus-lazos-la-abeja-sin-aguijon
https://ojo-publico.com/entrevistas/luciano-lopez-el-tc-es-el-guardian-las-decisiones-del-congreso
https://ojo-publico.com/5518/muertes-puno-los-seis-soldados-que-los-aymaras-aun-lloran
https://ojo-publico.com/politica/familiares-funcionarios-fueron-contratados-la-sunedu
https://ojo-publico.com/opinion/cartas-y-replicas/funcionario-del-serfor-dice-no-estar-investigado-caso-yacu-kallpa
https://ojo-publico.com/5504/los-guardianes-la-amazonia-arte-y-memoria-indigena-los-arboles
https://ojo-publico.com/entrevistas/ramirez-el-congreso-usa-infracciones-constitucionales-como-prefiere
https://ojo-publico.com/5501/narcomineria-la-historia-como-se-lava-dinero-las-drogas-oro
https://ojo-publico.com/entrevistas/colchado-un-abogado-presuntos-criminales-no-puede-ser-ministro
https://ojo-publico.com/derechos-humanos/pnp-separo-solo-por-inasistencia-policia-investigado-por-asesinato
https://ojo-publico.com/sala-del-poder/la-libertad-reporta-usd-2047-millones-vinculados-al-lavado-activos
https://ojo-publico.com/entrevistas/eduardo-dargent-el-ejecutivo-es-una-suerte-felpudo-del-congreso
https://ojo-publico.com/opinion/cartas-y-replicas/funcionario-del-serfor-niega-imputacion-delitos-ambientales
https://ojo-publico.com/entrevistas/neyra-cada-vez-hay-mas-indicios-para-que-vizcarra-pueda-ser-condenado
https://ojo-publico.com/5488/investigado-por-delitos-ambientales-evaluara-exportacion-madera
https://ojo-publico.com/ambiente/paracas-multas-por-s13-millones-pesqueras-riesgo-prescribir
https://ojo-publico.com/5489/unidades-pnp-investigacion-desmanteladas-e-infiltradas-por-crimen
https://ojo-publico.com/2772/lobby-y-demanda-el-destino-fatal-del-shihuahuaco-amazonico
https://ojo-publico.com/ambiente/territorio-amazonas/gobierno-se-opone-reconocimiento-territorio-indigenas-aislados
https://ojo-publico.com/entrevistas/trump-utiliza-la-amenaza-como-una-herramienta-politica-exterior
https://ojo-publico.com/5279/viaje-al-corazon-del-bosque-el-rostro-harakbut-madre-dios
https://ojo-publico.com/5468/la-espiral-del-desamparo-abogados-publicos-y-violencia-genero
https://ojo-publico.com/5479/ataque-la-fiscalia-punto-quiebre-la-violencia-urbana-peru
https://ojo-publico.com/entrevistas/ruben-vargas-el-gobierno-claudico-enfrentar-el-crimen-organizado
https://ojo-publico.com/5478/familiares-20-congresistas-sancionados-por-contratar-el-estado
https://ojo-publico.com/latinoamerica/corto-documental-dos-caras-la-filantropia-la-comida-chatarra
https://ojo-publico.com/5077/los-vinculos-ocho-sur-la-proveedora-la-multinacional-pepsico
https://ojo-publico.com/5435/peru-europa-opacidad-el-comercio-global-del-zinc
https://ojo-publico.com/5076/ocho-surs-links-palm-oil-supplier-multinational-pepsico
https://ojo-publico.com/ojobionico/las-versiones-falsas-y-ciertas-la-toma-posesion-donald-trump
https://ojo-publico.com/politica/gustavo-gutierrez-ticse-intervino-proceso-su-excliente-el-tc
https://ojo-publico.com/5473/mas-400-personas-ancash-tienen-metales-por-encima-del-limite
https://ojo-publico.com/entrevistas/vilca-los-actores-politicos-poder-tienen-pavor-las-elecciones
https://ojo-publico.com/politica/deficit-fiscal-al-alza-encamina-al-peru-hacia-deudas-mas-caras
https://ojo-publico.com/ambiente/pesca-ilegal-produce-impulsa-norma-que-afecta-investigaciones-penales
https://ojo-publico.com/5469/juliaca-dos-anos-una-historica-masacre
https://ojo-publico.com/entrevistas/manuel-burga-el-lugar-la-memoria-esta-para-indignarnos
https://ojo-publico.com/ojobionico/verificadores-america-latina-rechazan-version-meta
https://ojo-publico.com/politica/janet-tello-es-elegida-presidenta-del-pj-medio-crisis-politica
https://ojo-publico.com/5462/nueva-ley-agraria-beneficiara-sobre-todo-siete-grandes-empresas
https://ojo-publico.com/5457/la-estrategia-la-industria-comida-chatarra-por-deducir-impuestos
https://ojo-publico.com/5456/pueblos-aislamiento-269-evidencias-desmontan-el-negacionismo
https://ojo-publico.com/politica/congreso-cierra-legislatura-ataque-la-separacion-poderes
https://ojo-publico.com/5461/amazonia-concentra-el-40-los-casos-ninos-y-adolescentes-vih
https://ojo-publico.com/latinoamerica/crisis-energetica-ecuador-lecciones-la-region-andino-amazonica
https://ojo-publico.com/ojolab/barra-politica-seguimos-dialogando-sobre-ciudadania-y-democracia
https://ojo-publico.com/5452/superestructura-criminal-los-lobos-avanzan-peru-chile-y-colombia
https://ojo-publico.com/ojolab/estudiantes-fe-y-alegria-elaboran-piezas-contra-la-desinformacion
https://ojo-publico.com/ojolab/relatoria-periodismo-investigacion-contra-los-crimenes-ambientales
https://ojo-publico.com/ojolab/barra-politica-unete-al-dialogo-sobre-democracia-y-derechos
https://ojo-publico.com/entrevistas/victor-cubas-lo-que-pasa-ahora-es-mas-grave-que-lo-ocurrido-los-90
https://ojo-publico.com/ambiente/estudio-revela-deficiencias-areas-marinas-protegidas
https://ojo-publico.com/entrevistas/velazquez-las-jerarquias-culturales-estan-basadas-la-desigualdad
https://ojo-publico.com/5447/fiscalia-senala-48-policias-y-militares-por-asesinato-protestas
https://ojo-publico.com/aliadosas/hablan-los-aliadosas-el-periodismo-debe-incomodar-al-poder
https://ojo-publico.com/opinion/cartas-y-replicas/empresaria-pide-eliminar-reportaje-sobre-detencion-exgobernador
https://ojo-publico.com/4896/apurimac-el-inicio-una-represion-que-mato-49-personas-peru
https://ojo-publico.com/4844/un-ano-del-gobierno-boluarte-las-siete-horas-masacre-puno
https://ojo-publico.com/4765/adolescentes-la-mira-protesta-y-muerte-la-selva-central
https://ojo-publico.com/4769/asesinato-ayacucho-un-adolescente-y-las-patrullas-militares
https://ojo-publico.com/5438/las-dos-caras-la-filantropia-las-donaciones-ultraprocesados
https://ojo-publico.com/5442/gobierno-tramito-12-dias-norma-que-debilita-osiptel-y-ositran
https://ojo-publico.com/ambiente/territorio-amazonas/cumbre-indigena-la-defensoria-del-pueblo-convoco-negacionistas
https://ojo-publico.com/sala-del-poder/tabacaleras-son-las-que-mas-vapeadores-ingresan-al-peru
https://ojo-publico.com/5440/two-faces-philanthropy-cost-donations-ultraprocessed
https://ojo-publico.com/opinion/cartas-y-replicas/petroperu-responde-denuncia-sobre-derrame-petroleo-andoas
https://ojo-publico.com/5434/tiempos-resistencia-mujeres-indigenas-contra-las-violencias
https://ojo-publico.com/5414/familiares-30-congresistas-contratan-estado-pese-impedimentos
https://ojo-publico.com/ambiente/cop29/cop29-culmina-financiamiento-climatico-por-debajo-lo-esperado
https://ojo-publico.com/5431/el-peru-pierde-mas-s8-millones-por-falta-impuesto-vapeadores
https://ojo-publico.com/entrevistas/luis-miguel-castilla-peru-estamos-dominados-por-las-mafias
https://ojo-publico.com/node/5428
https://ojo-publico.com/node/5430
https://ojo-publico.com/node/5427
https://ojo-publico.com/node/5425
https://ojo-publico.com/node/5421
https://ojo-publico.com/node/5423
https://ojo-publico.com/node/5424
https://ojo-publico.com/node/5405
https://ojo-publico.com/node/5420
https://ojo-publico.com/node/5418
https://ojo-publico.com/5416/el-regreso-trump-posibles-impactos-su-desden-latinoamerica
https://ojo-publico.com/entrevistas/apec-no-va-cambiar-la-imagen-peru-el-plano-internacional
https://ojo-publico.com/5415/apec-2024-la-influencia-china-peru-y-los-retos-que-dejo-la-cumbre
https://ojo-publico.com/ambiente/cop29/cop29-una-semana-sin-consensos-sobre-el-financiamiento-climatico
https://ojo-publico.com/node/5412
https://ojo-publico.com/ambiente/cop29/cop29-el-reto-la-agenda-climatica-pendiente-un-pais-petrolero
https://ojo-publico.com/node/5409
https://ojo-publico.com/node/5411
https://ojo-publico.com/node/5407
https://ojo-publico.com/node/5408
https://ojo-publico.com/node/5403
https://ojo-publico.com/node/5402
https://ojo-publico.com/5215/india-detras-del-negocio-global-por-borrar-reportajes-ojopublico
https://ojo-publico.com/node/5400
https://ojo-publico.com/node/5399
https://ojo-publico.com/node/5397
https://ojo-publico.com/node/5396
https://ojo-publico.com/node/5394
https://ojo-publico.com/5392/nuevo-litigio-opaca-la-inauguracion-del-puerto-chancay
https://ojo-publico.com/entrevistas/susel-paredes-hay-un-pacto-autoritario-entre-los-poderes-del-estado
https://ojo-publico.com/5390/ciberdelincuencia-la-ruta-detras-del-robo-datos-interbank
https://ojo-publico.com/ojolab/barra-politica-las-identidades-tiempos-autoritarios
https://ojo-publico.com/politica/juez-del-tc-ataca-ojopublico-audiencia-sobre-nueva-ley-forestal
https://ojo-publico.com/politica/el-60-hogares-depende-la-informalidad-el-peru
https://ojo-publico.com/entrevistas/patricia-paniagua-una-coalicion-el-poder-protege-las-mafias
https://ojo-publico.com/5379/congreso-impulsa-decena-proyectos-para-someter-sistema-justicia
https://ojo-publico.com/ambiente/cop16-dos-acuerdos-el-lento-camino-para-proteger-la-biodiversidad
https://ojo-publico.com/5382/narcotrafico-y-deforestacion-crecen-zonas-pueblos-aislamiento
https://ojo-publico.com/opinion/cartas-y-replicas/ocho-sur-senala-nueva-carta-no-tener-vinculos-deforestacion
https://ojo-publico.com/5377/bancos-acumulan-mas-s7-millones-multas-por-malos-servicios
https://ojo-publico.com/5368/puerto-chancay-cosco-shipping-no-reconoce-competencias-ositran
https://ojo-publico.com/5374/los-secretos-la-profeta-del-petroleo-la-venezuela-maduro
https://ojo-publico.com/ambiente/maccarthy-alertas-incendios-la-amazonia-aumentaron-79
https://ojo-publico.com/entrevistas/salomon-lerner-corremos-el-riesgo-volver-la-epoca-violencia
https://ojo-publico.com/ambiente/cop16-el-mecanismo-que-confronta-paises-ricos-los-megadiversos
https://ojo-publico.com/opinion/cartas-y-replicas/postulante-la-jnj-explica-su-vinculo-exalcalde-chiclayo
https://ojo-publico.com/politica/miembros-del-tc-aumentaron-su-patrimonio-solo-dos-anos
https://ojo-publico.com/ambiente/peru-llega-cop16-biodiversidad-metas-pero-sin-una-estrategia
https://ojo-publico.com/entrevistas/dante-vera-estamos-ante-un-problema-seguridad-nacional
https://ojo-publico.com/ojolab/barra-politica-desborde-extorsiones-vulnerabilidad-e-inseguridad
https://ojo-publico.com/ambiente/cop16-las-voces-indigenas-amazonicas-las-negociaciones
https://ojo-publico.com/politica/las-sanciones-la-universidad-que-elaboro-el-examen-para-la-jnj
https://ojo-publico.com/5320/desborde-extorsiones-y-homicidios-una-policia-precarizada
https://ojo-publico.com/opinion/cartas-y-replicas/cosco-shipping-envia-carta-por-segundo-reportaje-del-puerto-chancay
https://ojo-publico.com/politica/los-nexos-entre-el-superintendente-y-los-nuevos-directores-sunedu
https://ojo-publico.com/politica/rodrigo-gil-los-que-van-ganando-el-2026-son-los-conservadores
https://ojo-publico.com/ambiente/produce-analiza-regulacion-anchoveta-ante-reportes-pesca-falsos
https://ojo-publico.com/latinoamerica/asesinato-peruano-por-militares-mexicanos-expone-crisis-migratoria
https://ojo-publico.com/politica/protestas-contra-extorsiones-ponen-jaque-al-congreso-y-al-gobierno
https://ojo-publico.com/5323/el-controvertido-camino-para-la-exclusividad-el-puerto-chancay
https://ojo-publico.com/5321/el-rio-amazonas-languidece-la-peor-sequia-mas-un-siglo
https://ojo-publico.com/entrevistas/avelino-guillen-quieren-tener-un-sistema-electoral-identico-al-2000
https://ojo-publico.com/5319/musk-controla-el-internet-del-96-municipios-amazonicos-brasil
https://ojo-publico.com/opinion/cartas-y-replicas/funcionario-del-minem-solicita-eliminar-articulos-ojopublico
https://ojo-publico.com/derechos-humanos/sin-luz-la-amazonia-brechas-energia-impactan-al-pueblo-awajun
https://ojo-publico.com/entrevistas/nicolas-zevallos-la-inseguridad-puede-llevar-al-autoritarismo
https://ojo-publico.com/ojolab/inicia-primer-encuentro-latinoamericano-periodismo-por-la-amazonia
https://ojo-publico.com/5313/areas-afectadas-por-incendios-forestales-crecieron-62-cuatro-anos
https://ojo-publico.com/politica/abogados-sin-experiencia-detras-del-examen-para-acceder-la-jnj
https://ojo-publico.com/ojolab/muestra-cuando-los-bosques-lloran-martires-defensores-ambientales
https://ojo-publico.com/ambiente/produce-archiva-al-menos-nueve-casos-por-reportes-pesca-incorrectos
https://ojo-publico.com/entrevistas/julissa-mantilla-la-ley-impunidad-es-una-amnistia-no-encubierta
https://ojo-publico.com/ambiente/territorio-amazonas/fallecidos-e-investigados-por-lavado-activos-aparecen-el-reinfo
https://ojo-publico.com/ambiente/territorio-amazonas/estudio-identifica-zonas-alto-contenido-carbono-la-amazonia
https://ojo-publico.com/entrevistas/farid-kahhat-lo-problematico-del-fujimorismo-se-queda-keiko
https://ojo-publico.com/5300/legado-autoritario-alberto-fujimori-fallecio-los-86-anos
https://ojo-publico.com/opinion/cartas-y-replicas/cosco-shipping-responde-reportaje-sobre-el-megapuerto-chancay
https://ojo-publico.com/5297/la-historia-detras-la-expansion-del-megapuerto-chancay
https://ojo-publico.com/politica/sanciones-e-incremento-patrimonial-candidatos-la-jnj
https://ojo-publico.com/5296/la-prescripcion-amenaza-el-caso-mas-grande-trafico-madera
https://ojo-publico.com/5267/el-tiempo-del-dragon-el-trafico-la-tortuga-matamata-sudamerica
https://ojo-publico.com/ambiente/fiscalia-incauta-barco-hayduk-valorizado-mas-usd-17-millones
https://ojo-publico.com/ojolab/ojopublico-celebra-10-anos-encuentro-internacional-y-un-festival
https://ojo-publico.com/5262/las-casas-sin-luz-paradojas-la-transicion-energetica-peru
https://ojo-publico.com/entrevistas/roxana-barrantes-crecer-3-no-ayuda-mejorar-la-vida-las-personas
https://ojo-publico.com/ambiente/territorio-amazonas/algoritmos-ilegalidad-la-madera-contradicen-cifras-oficiales
https://ojo-publico.com/5287/los-nexos-entre-postulantes-la-jnj-y-casos-organizacion-criminal
https://ojo-publico.com/ambiente/territorio-amazonas/cartografia-indigena-el-conocimiento-los-maijunas-su-territorio
https://ojo-publico.com/5290/reduccion-igv-restaurantes-se-dejo-recaudar-s1400-millones
https://ojo-publico.com/opinion/cartas-y-replicas/funcionarios-minem-responden-denuncia-nexos-mineria-ilegal
https://ojo-publico.com/5273/pecado-e-impunidad-abusos-sexuales-la-iglesia-catolica-mexico
https://ojo-publico.com/entrevistas/jose-ugaz-los-cambios-la-ley-responden-al-crimen-organizado
https://ojo-publico.com/ambiente/denuncia-interna-del-minem-expone-presuntos-nexos-mineria-ilegal
https://ojo-publico.com/politica/mas-s189000-para-la-defensa-legal-congresistas-investigados
https://ojo-publico.com/5281/reportes-pesca-falsos-y-cambios-produce-acorralan-la-anchoveta
https://ojo-publico.com/entrevistas/mariana-heredia-la-democracia-se-ha-vaciado-contenido
https://ojo-publico.com/5270/jnj-ratifico-resoluciones-jueces-y-fiscales-pese-irregularidades
https://ojo-publico.com/ambiente/territorio-amazonas/produce-apela-fallo-del-pj-para-no-brindar-datos-publicos-madereras
https://ojo-publico.com/5269/el-centro-del-crimen-transnacional-por-el-oro-ilegal-ecuador
https://ojo-publico.com/ojobionico/explicador-esto-dice-la-ley-sobre-el-delito-encubrimiento
https://ojo-publico.com/politica/las-tres-investigaciones-por-corrupcion-eduardo-salhuana
https://ojo-publico.com/5259/ashaninkas-del-vraem-defienden-sus-tierras-las-abejas-sin-aguijon
https://ojo-publico.com/entrevistas/omar-coronel-la-protesta-necesita-el-insumo-la-esperanza
https://ojo-publico.com/5263/desigualdad-peru-las-demandas-ignoradas-un-pais-fracturado
https://ojo-publico.com/5250/chequealo-ojopublico-estrena-un-programa-contra-la-desinformacion
https://ojo-publico.com/politica/congreso-promulga-leyes-impunidad-y-favor-del-crimen-organizado
https://ojo-publico.com/ojolab/tres-investigaciones-ojopublico-son-finalistas-premios-sip
https://ojo-publico.com/5027/ayahuasca-entre-la-tradicion-ancestral-y-el-oportunismo-comercial
https://ojo-publico.com/ojolab/unete-la-charla-sobre-los-retos-la-recaudacion-tributaria
https://ojo-publico.com/entrevistas/natalia-gonzalez-nuestras-autoridades-nos-han-traicionado
https://ojo-publico.com/5243/alertas-por-corrupcion-dentro-proximo-ministerio-infraestructura
https://ojo-publico.com/5244/elecciones-2024-venezuela-esta-crisis-no-es-un-deja-vu
https://ojo-publico.com/5229/los-sellos-alimenticios-una-industria-que-crece-sin-control
https://ojo-publico.com/latinoamerica/un-acuerdo-que-no-protege-pueblos-amazonicos-expuestos-biopirateria
https://ojo-publico.com/5129/el-habito-pensar-tiempos-criticos-desafios-para-la-filosofia
https://ojo-publico.com/5235/un-sistema-que-facilita-el-lavado-oro-y-un-congreso-que-lo-defiende
https://ojo-publico.com/ambiente/territorio-amazonas/exponen-irregularidades-reconocimiento-comunidad-fantasma
https://ojo-publico.com/entrevistas/joseph-dager-estamos-un-autoritarismo-gobernado-por-el-congreso
https://ojo-publico.com/latinoamerica/taxista-operador-del-narcotrafico-entre-colombia-y-ecuador
https://ojo-publico.com/entrevistas/alban-dina-boluarte-la-estan-haciendo-respirar-artificialmente
https://ojo-publico.com/ambiente/territorio-amazonas/empresas-sin-permiso-ambiental-podran-acogerse-nuevo-reglamento
https://ojo-publico.com/politica/amnistia-internacional-pide-investigar-boluarte-por-autoria-mediata
https://ojo-publico.com/225/dea-y-dirandro-detras-del-contacto-tocache-fuerza-popular
https://ojo-publico.com/entrevistas/juan-jimenez-hay-un-retroceso-el-respeto-los-derechos-humanos
https://ojo-publico.com/politica/nombramientos-cancilleria-refuerzan-alianza-el-fujimorismo
https://ojo-publico.com/ambiente/territorio-amazonas/la-tala-ilegal-y-narcotrafico-acechan-los-defensores-la-amazonia
https://ojo-publico.com/sala-del-poder/essalud-y-universidad-alas-peruanas-entre-las-mas-multadas-por-sunafil
https://ojo-publico.com/politica/ausencia-barata-juicios-limita-el-analisis-sus-confesiones
https://ojo-publico.com/5207/peru-flexibilizo-pesca-anchoveta-juvenil-sin-sustento-cientifico
https://ojo-publico.com/5208/universidades-san-martin-y-telesup-adeudan-s178-millones-multas
https://ojo-publico.com/politica/cambios-del-mef-al-deficit-fiscal-permitiran-el-descontrol-del-gasto
https://ojo-publico.com/entrevistas/segura-debil-manejo-fiscal-puede-gatillar-rebajas-calificacion
https://ojo-publico.com/aliadosas/aliadosas-estrena-nuevo-logo-y-renueva-su-compromiso-la-verdad
https://ojo-publico.com/ambiente/territorio-amazonas/policia-tiene-concesion-minera-zona-indigena-donde-operan-ilegales
https://ojo-publico.com/5007/estado-claudica-amazonas-mineria-ilegal-financia-obras-cenepa
https://ojo-publico.com/5062/india-y-emiratos-arabes-unidos-nuevos-destinos-del-oro-sucio-peruano
https://ojo-publico.com/4600/la-maldicion-del-oro-la-cuenca-amazonica-del-rio-nanay
https://ojo-publico.com/ambiente/territorio-amazonas/una-demanda-busca-proteger-el-rio-nanay-y-anular-concesion-minera
https://ojo-publico.com/ambiente/territorio-amazonas/los-nexos-entre-las-joyerias-iquitos-y-el-oro-ilegal-del-rio-nanay
https://ojo-publico.com/5201/congreso-aprobo-mas-25-leyes-que-afectan-la-institucionalidad
https://ojo-publico.com/politica/municipalidad-lima-deposito-dinero-bonos-scotiabank-y-banbif
https://ojo-publico.com/ambiente/territorio-amazonas/pueblos-indigenas-y-fauna-amenazados-por-actividades-ilicitas
https://ojo-publico.com/edicion-regional/southern-sustenta-la-licencia-social-tia-maria-carta-del-minem
https://ojo-publico.com/5175/raptados-la-historia-olvidada-los-ninos-la-guerra-peru
https://ojo-publico.com/entrevistas/ana-neyra-tenemos-un-estado-que-promueve-la-impunidad
https://ojo-publico.com/5199/clanes-la-topa-y-sus-redes-la-madera-amazonica-peru-y-ecuador
https://ojo-publico.com/5153/el-hambre-avanza-las-ciudades-caen-los-ingresos-zonas-urbanas
https://ojo-publico.com/5177/los-bancos-del-peru-que-financian-combustibles-fosiles-la-amazonia
https://ojo-publico.com/politica/alberto-fujimori-podra-ser-acusado-por-nuevos-casos-lesa-humanidad
https://ojo-publico.com/5137/cientificas-extraen-adn-del-aire-para-identificar-especies-amazonicas
https://ojo-publico.com/entrevistas/leyla-huerta-hay-muestras-una-legislacion-que-busca-exterminarnos
https://ojo-publico.com/entrevistas/la-puente-creo-que-estan-cerca-lograr-la-salida-la-corte-idh
https://ojo-publico.com/5170/los-crimenes-lesa-humanidad-que-el-congreso-busca-que-prescriban
https://ojo-publico.com/5162/legado-historico-abandono-mas-60-zonas-arqueologicas-amenazadas
https://ojo-publico.com/5172/concesiones-mineras-se-duplicaron-la-amazonia-peruana
https://ojo-publico.com/ojolab/ojopublico-aparece-entre-las-principales-marcas-mediaticas-del-peru
https://ojo-publico.com/politica/congreso-cierra-sesiones-ocho-proyectos-contra-institucionalidad
https://ojo-publico.com/edicion-regional/asesinatos-lideres-la-amazonia-amenazan-el-buen-vivir-indigena
https://ojo-publico.com/5160/los-asesores-fuerza-popular-puestos-clave-el-gobierno
https://ojo-publico.com/5164/pueblos-aymaras-entre-el-miedo-y-desconfianza-por-concesiones-mineras
https://ojo-publico.com/5166/grupos-armados-amenazan-el-exterminio-del-pueblo-indigena-siona
https://ojo-publico.com/latinoamerica/latinoamerica-se-ha-convertido-incubadora-del-crimen-organizado
https://ojo-publico.com/4728/la-casa-los-chequeos-un-reality-contra-la-desinformacion
https://ojo-publico.com/5138/creencias-disputa-el-avance-la-objecion-conciencia
https://ojo-publico.com/latinoamerica/los-cinco-grandes-bancos-que-hacen-greenwashing-la-amazonia
https://ojo-publico.com/5155/algorithm-alerts-high-risks-illegality-amazonian-timber
https://ojo-publico.com/5134/credicorp-y-bank-america-detras-emision-bonos-lima
https://ojo-publico.com/5152/narcodeforestacion-el-nuevo-mapa-la-coca-destruye-la-amazonia
https://ojo-publico.com/5157/narco-deforestation-new-coca-map-destroys-andean-amazon
https://ojo-publico.com/5151/pandilleros-fuga-el-exodo-la-ms-13-ante-el-regimen-bukele
https://ojo-publico.com/node/5156
https://ojo-publico.com/sala-del-poder/repsol-del-derrame-el-mar-la-empresa-mas-ingresos-el-2023
https://ojo-publico.com/5124/circulos-intimos-los-nexos-entre-dina-boluarte-y-patricia-benavides
https://ojo-publico.com/5100/patricia-benavides-busco-obstruir-proceso-por-llamadas-camayo
https://ojo-publico.com/ojolab/ojopublico-la-conferencia-del-dia-mundial-la-libertad-prensa
https://ojo-publico.com/ojolab/fe-y-alegria-incorpora-el-factchecking-su-programas-estudios
https://ojo-publico.com/ambiente/expansion-urbana-y-concesiones-afectan-11-los-14-humedales-ramsar
https://ojo-publico.com/ojolab/taller-apreciacion-documentales-hector-galvez
https://ojo-publico.com/5144/bolivia-financio-medios-afines-contratos-publicidad
https://ojo-publico.com/5142/los-millonarios-intereses-pesqueros-detras-la-anchoveta-paracas
https://ojo-publico.com/5149/los-14-estudios-que-defienden-politicos-investigados-por-corrupcion
https://ojo-publico.com/latinoamerica/crece-oposicion-indigena-contra-explotacion-petroleo-la-amazonia
https://ojo-publico.com/politica/bank-america-cobro-s97-millones-por-emision-bonos-lima
https://ojo-publico.com/edicion-regional/desnutricion-y-anemia-crecen-la-par-la-hoja-coca-el-vraem
https://ojo-publico.com/ojobionico/chequealo-ojopublico-lanza-programa-concurso-contra-la-desinformacion
https://ojo-publico.com/politica/jnj-destituye-patricia-benavides-por-favorecer-su-hermana
https://ojo-publico.com/ambiente/territorio-amazonas/crean-comunidades-fantasma-la-amazonia-aval-autoridades
https://ojo-publico.com/5127/mas-s40-millones-perdidos-por-medicamentos-vencidos-cuatro-anos
https://ojo-publico.com/ojolab/ojopublico-se-suma-selecto-grupo-medios-para-investigar-el-crimen
https://ojo-publico.com/latinoamerica/oro-sucio-policias-involucrados-trafico-combustible-ecuador
https://ojo-publico.com/entrevistas/patricia-zarate-esta-riesgo-que-tengamos-elecciones-limpias
https://ojo-publico.com/ambiente/territorio-amazonas/mineria-ilegal-y-narcotrafico-detras-del-crimen-victorio-dariquebe
https://ojo-publico.com/5116/encuentros-secretos-reuniones-boluarte-y-gobernadores-sin-registro
https://ojo-publico.com/latinoamerica/estudio-halla-bacterias-resistentes-antibioticos-rio-ecuador
https://ojo-publico.com/entrevistas/godoy-el-unico-programa-gobierno-boluarte-es-sobrevivir
https://ojo-publico.com/entrevistas/hay-un-interes-la-politica-intervenir-el-sistema-electoral
https://ojo-publico.com/entrevistas/ana-estrada-siempre-busco-que-su-conquista-marcara-un-precedente
https://ojo-publico.com/latinoamerica/oro-ilegal-nuevas-tecnologias-para-rastrear-origen-se-quedan-cortas
https://ojo-publico.com/opinion/cartas-y-replicas/ocho-sur-niega-perdida-bosques-sobre-territorios-donde-opera
https://ojo-publico.com/4406/exportadores-la-amazonia-deberan-garantizar-que-no-deforestan
https://ojo-publico.com/sala-del-poder/derrame-repsol-organizaciones-enfrentan-la-junta-accionistas
https://ojo-publico.com/politica/hermano-y-abogado-boluarte-son-detenidos-por-trafico-influencias
https://ojo-publico.com/politica/pobreza-peru-alcanzo-al-29-poblacion-2023
https://ojo-publico.com/ojobionico/sentenciados-como-alberto-fujimori-no-pueden-postular-la-presidencia
https://ojo-publico.com/derechos-humanos/salud/vacunagate-44-funcionarios-y-medicos-sancionados-tres-anos
https://ojo-publico.com/5043/casi-medio-millon-escolares-se-abastecen-agua-rios-y-lluvias
https://ojo-publico.com/politica/seis-jueces-implicados-investigacion-contra-patricia-benavides
https://ojo-publico.com/ojolab/ojopublico-vivo-ayacucho-conversatorio-sobre-democracia-y-ddhh
https://ojo-publico.com/politica/congreso-citara-lopez-aliaga-y-al-mef-por-sobrendeudamiento-lima
https://ojo-publico.com/5080/las-casas-vacias-crisis-climatica-y-migracion-el-altiplano-peruano
https://ojo-publico.com/opinion/cartas-y-replicas/empresa-em-company-responde-reportaje-sobre-las-rutas-del-oro
https://ojo-publico.com/politica/boluarte-retira-al-presidente-del-consejo-fiscal-tras-criticas-al-mef
https://ojo-publico.com/5081/millonaria-deuda-lima-financia-obras-duplicadas-y-sin-expedientes
https://ojo-publico.com/5065/la-evolucion-la-debida-diligencia-del-oro-la-lbma
https://ojo-publico.com/5060/gold-companies-linked-illegal-mining-colombian-amazon
https://ojo-publico.com/5030/las-empresas-oro-y-la-mineria-ilegal-la-amazonia-colombia
https://ojo-publico.com/5070/india-and-united-arab-emirates-new-destinations-peruvian-gold
https://ojo-publico.com/node/5072
https://ojo-publico.com/5059/organized-crime-groups-behind-new-amazon-illegal-mining-enclaves
https://ojo-publico.com/5067/evolution-gold-due-diligence-lbma
https://ojo-publico.com/5068/itaituba-capital-gold-laundering-brazilian-amazon
https://ojo-publico.com/node/5073
https://ojo-publico.com/5031/oro-sucio-companias-exportadoras-ecuador-la-mira-autoridades
https://ojo-publico.com/5055/itaituba-la-capital-del-lavado-oro-la-amazonia-brasil
https://ojo-publico.com/5058/crimen-organizado-y-sus-vinculos-la-mineria-ilegal-la-amazonia
https://ojo-publico.com/5029/la-invasion-las-dragas-y-el-oro-origen-desconocido-bolivia
https://ojo-publico.com/5071/dirty-gold-ecuadorian-export-companies-targeted-authorities
https://ojo-publico.com/5056/dredge-invasion-and-tons-gold-unknown-origin-bolivia
https://ojo-publico.com/5039/los-abusos-detras-del-negocio-la-produccion-langostinos-india
https://ojo-publico.com/5047/el-acelerado-incremento-las-fortunas-los-ministros-boluarte
https://ojo-publico.com/1107/metalor-financio-cargas-toneladas-oro-ilegal-peru
https://ojo-publico.com/5022/la-voraz-demanda-la-acuicultura-pone-jaque-la-anchoveta
https://ojo-publico.com/node/2147
https://ojo-publico.com/4996/seguros-salud-miles-reclamos-y-escasas-sanciones"""

final_result = text.split('\n')

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
