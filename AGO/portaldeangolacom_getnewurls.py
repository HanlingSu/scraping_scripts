# Packages:
import sys
import os
import re
import getpass
from typing import final
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np 
from tqdm import tqdm

from pymongo import MongoClient


import bs4
from bs4 import BeautifulSoup
from newspaper import Article
from dateparser.search import search_dates
import dateparser
import requests
from urllib.parse import quote_plus

import urllib.request
import time
from time import time
import random
from random import randint, randrange
from warnings import warn
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

# db connection:
db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p

direct_URLs = []

base = 'https://www.portaldeangola.com/post-sitemap'

# for year in range(2022, 2023):
#     year_str = str(year)
#     for month in range(8, 12):
#         if month < 10:
#             month_str = '0' + str(month)
#         else:
#             month_str = str(month)
#         sitemap = base + year_str +'-' + month_str +'.xml'
#         print(sitemap)
#         hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
#         req = requests.get(sitemap, headers = hdr)
#         soup = BeautifulSoup(req.content)
#         item = soup.find_all('loc')
#         for i in item:
#             url = i.text
#             direct_URLs.append(url)

#         print(len(direct_URLs))

# for i in range(1, 3):
#         sitemap = base + str(i) + '.xml'
#         print(sitemap)
#         hdr = {'User-Agent': 'Mozilla/5.0'} #header settings
#         req = requests.get(sitemap, headers = hdr)
#         soup = BeautifulSoup(req.content)
#         item = soup.find_all('loc')
#         for i in item:
#             url = i.text
#             direct_URLs.append(url)

#         print(len(direct_URLs))


text = """https://www.portaldeangola.com/blog/
https://www.portaldeangola.com/cristovao-colombo-era-espanhol-e-judeu-revela-novo-estudo/
https://www.portaldeangola.com/secretario-geral-da-onu-ataques-contra-unifil-podem-constituir-crime-de-guerra/
https://www.portaldeangola.com/abel-chivukuvuku-esta-de-regresso-a-ribalta-da-politica-angolana/
https://www.portaldeangola.com/candidato-independente-nas-eleicoes-de-mocambique-ameaca-greve-nacional-se-a-frelimo-vencer/
https://www.portaldeangola.com/a-fitch-ratings-colocou-a-notacao-de-credito-da-franca-numa-perspectiva-negativa-devido-ao-elevado-defice-orcamental/
https://www.portaldeangola.com/presidente-joao-lourenco-conversa-com-joe-biden-sobre-novas-datas-para-a-visita-a-angola/
https://www.portaldeangola.com/sul-africanos-mais-optimistas-quanto-ao-futuro-da-economia-desde-a-formacao-do-governo-de-unidade-nacional/
https://www.portaldeangola.com/a-rd-congo-quer-reduzir-o-controlo-da-china-sobre-o-sector-mineiro-e-apostar-fortemente-no-corredor-do-lobito/
https://www.portaldeangola.com/o-crescimento-das-energias-renovaveis-ate-2030-devera-igualar-a-capacidade-energetica-actual-das-maiores-economias-diz-aie/
https://www.portaldeangola.com/na-hora-da-despedida-de-um-jornalista-que-sempre-quis-ser-cidadao/
https://www.portaldeangola.com/as-consequencias-do-proximo-ajustamento-estatutario-do-mpla/
https://www.portaldeangola.com/alemanha-podera-sofrer-contraccao-economica-pelo-segundo-ano-consecutivo/
https://www.portaldeangola.com/foco-no-apoio-as-pme-kagame-diz-aos-lideres-africanos-na-conferencia-biashara-afrika-2024/
https://www.portaldeangola.com/varios-tornados-anunciam-a-chegada-do-furacao-do-seculo-milton-e-causam-panico-na-florida/
https://www.portaldeangola.com/presidente-dos-estados-unidos-vai-visitar-angola-em-data-a-anunciar/
https://www.portaldeangola.com/biden-critica-trump-por-ataque-de-mentiras-sobre-os-furacoes/
https://www.portaldeangola.com/viktor-orban-e-ursula-von-der-leyen-em-debate-aceso-no-parlamento-europeu/
https://www.portaldeangola.com/presidente-mexicana-rejeita-retorno-da-guerra-contra-o-trafico-de-drogas-no-mexico/
https://www.portaldeangola.com/supremo-brasileiro-autoriza-regresso-imediato-da-rede-social-x-ao-brasil/
https://www.portaldeangola.com/petroleo-cai-apos-forte-subida-enquanto-a-china-retem-novos-estimulos-e-o-medio-oriente-mantem-se-num-impasse/
https://www.portaldeangola.com/legisladores-quenianos-votam-a-favor-do-impeachment-do-vice-presidente-do-pais/
https://www.portaldeangola.com/adiado-o-sonho-impactos-do-adiamento-da-visita-de-joe-biden-a-angola-e-as-expectativas-do-governo-angolano/
https://www.portaldeangola.com/desafios-para-a-criacao-de-uma-agencia-de-notacao-de-credito-em-africa/
https://www.portaldeangola.com/mocambique-vai-amanha-as-eleicoes-presidenciais-num-clima-de-tensao-politica-e-dificuldades-economicas/
https://www.portaldeangola.com/sombra-do-metoo-paira-sobre-industria-da-musica/
https://www.portaldeangola.com/conseguira-netanyahu-manter-o-apoio-interno-enquanto-israel-luta-em-varias-frentes/
https://www.portaldeangola.com/empresas-nigerianas-reduzem-divida-em-dolares-enquanto-naira-continua-a-cair-face-ao-dolar/
https://www.portaldeangola.com/bp-aumenta-producao-de-petroleo-e-gas-revertendo-a-politica-anterior-de-reducao-da-producao-ate-2030/
https://www.portaldeangola.com/senegal-promete-acao-rapida-para-reduzir-o-defice-orcamental-e-controlar-a-divida-publica/
https://www.portaldeangola.com/o-crescimento-do-emprego-nos-eua-supera-todas-as-estimativas-deixando-a-fed-em-alerta/
https://www.portaldeangola.com/comissao-europeia-obtem-apoio-dos-estados-membros-da-eu-para-impor-tarifas-ate-45-sobre-veiculos-eletricos-chineses/
https://www.portaldeangola.com/milhares-marcham-em-londres-em-apoio-a-gaza-um-ano-depois-de-7-de-outubro/
https://www.portaldeangola.com/politica-externa-expoe-divisoes-no-regime-iraniano/
https://www.portaldeangola.com/angola-entre-os-paises-africanos-produtores-de-petroleo-que-mobilizaram-45-do-capital-inicial-do-banco-africano-de-energia/
https://www.portaldeangola.com/preco-do-petroleo-dispara-depois-de-biden-dizer-que-os-eua-estao-a-discutir-ataque-israelita-as-instalacoes-do-irao/
https://www.portaldeangola.com/ha-36-anos-a-alemanha-oriental-e-ocidental-reuniram-se-apos-45-anos-de-separacao-no-rescaldo-da-segunda-guerra-mundial/
https://www.portaldeangola.com/ue-toma-medidas-para-adiar-regra-da-desflorestacao-em-resposta-aos-apelos-dos-parceiros-mundiais/
https://www.portaldeangola.com/centro-carter-apresenta-atas-das-eleicoes-venezuelanas-na-oea/
https://www.portaldeangola.com/promotor-considera-privada-conduta-de-trump-para-tentar-anular-eleicoes-de-2020/
https://www.portaldeangola.com/guine-bissau-esta-a-usar-tecnologia-blockchain-para-aumentar-a-transparencia-fiscal/
https://www.portaldeangola.com/os-precos-do-petroleo-sobem-face-ao-risco-de-escalada-no-conflito-israel-e-irao/
https://www.portaldeangola.com/novo-reves-para-os-brics-argelia-abandonou-candidatura-para-integrar-os-brics/
https://www.portaldeangola.com/antonio-guterres-considerado-persona-non-grata-e-proibido-de-entrar-em-israel/
https://www.portaldeangola.com/inflacao-na-zona-euro-cai-abaixo-dos-2-apoiando-as-expectativas-de-cortes-nas-taxas-de-juro-do-bce/
https://www.portaldeangola.com/egito-e-etiopia-rejeitam-declaracao-dos-brics-sobre-proposta-de-lugares-no-conselho-de-seguranca-da-onu-para-africa/
https://www.portaldeangola.com/como-o-reino-unido-se-tornou-o-primeiro-pais-do-g7-a-eliminar-totalmente-a-energia-a-carvao/
https://www.portaldeangola.com/irao-lanca-misseis-contra-israel-sirenes-tocam-o-alerta-em-todo-o-pais/
https://www.portaldeangola.com/bolsas-da-china-sobem-no-maior-rali-num-so-dia-desde-2008-devido-aos-estimulos-economicos-do-governo/
https://www.portaldeangola.com/adnoc-dos-emirados-arabes-unidos-investe-na-industria-petroquimica-alema/
https://www.portaldeangola.com/corredor-do-lobito-o-paradoxo-dos-recursos-naturais-da-republica-democratica-do-congo/
https://www.portaldeangola.com/a-nigeria-e-chamada-a-liderar-em-nome-de-africa-no-conselho-de-seguranca-da-onu-diz-o-ministro-dos-negocios-estrangeiros/
https://www.portaldeangola.com/principais-empresas-petroliferas-dos-eua-revelam-pagamentos-macicos-a-governos-estrangeiros/
https://www.portaldeangola.com/israel-lanca-ataques-terrestres-contra-o-hezbollah-no-libano/
https://www.portaldeangola.com/75-anos-da-revolucao-comunista-na-china-o-milagre-economico-que-fez-de-pais-pobre-uma-superpotencia-global/
https://www.portaldeangola.com/a-venezuela-de-maduro-e-insustentavel-afirma-lider-opositora/
https://www.portaldeangola.com/moradores-das-centralidades-que-nao-pagam-rendas-com-ameaca-de-despejo/
https://www.portaldeangola.com/isabel-dos-santos-perde-apelo-contra-congelamento-de-centenas-de-milhoes-de-dolares/
https://www.portaldeangola.com/a-urgencia-de-combater-a-pobreza-energetica-como-o-g20-pode-contribuir-para-o-acesso-universal-a-energia-limpa-para-cozinhar/
https://www.portaldeangola.com/vendas-de-veiculos-eletricos-cairam-na-europa-e-nos-eua/
https://www.portaldeangola.com/ue-decide-a-4-de-outubro-se-vai-impor-tarifas-sobre-veiculos-eletricos-chineses/
https://www.portaldeangola.com/assassinato-de-nasrallah-revela-profundidade-da-infiltracao-de-israel-no-hezbollah/
https://www.portaldeangola.com/presidente-joao-lourenco-lamenta-morte-de-dom-alexandre-do-nascimento/
https://www.portaldeangola.com/hezbollah-confirma-que-o-seu-lider-hassan-nasrallah-foi-morto-num-ataque-de-israel/
https://www.portaldeangola.com/israel-diz-ter-matado-o-lider-do-hezbollah-nasrallah-abrindo-uma-pagina-perigosa-no-conflito-no-medio-oriente/
https://www.portaldeangola.com/brasil-x-afirma-que-cumpriu-exigencias-judiciais-e-pede-desbloqueio-da-plataforma-no-brasil/
https://www.portaldeangola.com/investimento-chines-em-angola-passa-barreira-dos-usd-24-mil-milhoes/
https://www.portaldeangola.com/china-da-ajuda-financeira-directa-a-cidadao-para-impulsionar-a-economia-e-melhorar-a-confianca-do-consumidor/
https://www.portaldeangola.com/exxon-vai-relancar-producao-de-petroleo-na-nigeria-com-investimento-de-10-mil-milhoes-de-dolares/
https://www.portaldeangola.com/opep-anuncia-aumento-da-producao-de-petroleo-em-dezembro-enquanto-os-precos-caem-perto-de-3/
https://www.portaldeangola.com/um-grupo-de-22-paises-incluindo-angola-tornou-se-a-maior-fonte-de-receitas-liquidas-do-fmi-excedendo-os-custos-operacionais-do-fundo/
https://www.portaldeangola.com/a-implantacao-de-energias-renovaveis-corre-o-risco-de-ficar-aquem-das-metas-globais-se-nao-houver-mais-dinheiro/
https://www.portaldeangola.com/a-minilua-que-vai-entrar-na-orbita-terrestre-por-2-meses/
https://www.portaldeangola.com/franca-propoe-cessar-fogo-de-21-dias-no-libano/
https://www.portaldeangola.com/russia-reve-a-doutrina-nuclear-com-um-novo-aviso-ao-ocidente/
https://www.portaldeangola.com/meta-inclui-vozes-celebres-em-chatbot-de-ia-e-apresenta-oculos-de-realidade-aumentada/
https://www.portaldeangola.com/zelenskiy-questiona-interesse-de-brasil-e-china-em-buscar-paz-na-ucrania/
https://www.portaldeangola.com/a-industria-de-cimento-comeca-a-investir-em-alternativas-de-producao-verde/
https://www.portaldeangola.com/governo-de-coligacao-da-africa-do-sul-mobiliza-investimentos-para-relancar-a-maior-economia-de-africa/
https://www.portaldeangola.com/joe-biden-visita-angola-de-13-a-15-de-outubro/
https://www.portaldeangola.com/nao-ha-paz-sem-dialogo-e-sem-concessoes-diz-joao-lourenco-na-onu/
https://www.portaldeangola.com/agt-anuncia-imposto-unico-para-empresas-em-2025/
https://www.portaldeangola.com/angola-novamente-em-rota-de-colisao-com-os-direitos-humanos/
https://www.portaldeangola.com/aumentam-as-preocupacoes-com-os-defices-fiscais-do-senegal-antes-das-eleicoes-de-novembro/
https://www.portaldeangola.com/tsmc-e-samsung-ponderam-construir-fabricas-de-chips-nos-emirados-arabes-unidos-diz-wsj/
https://www.portaldeangola.com/intel-recebe-oferta-multibilionaria-da-apollo-enquanto-a-qualcomm-planeia-aquisicao/
https://www.portaldeangola.com/pr-advoga-na-onu-sistema-financeiro-internacional-mais-justo/
https://www.portaldeangola.com/a-microsoft-e-a-blackrock-lancam-parceria-num-fundo-de-us-30-mil-milhoes-para-a-financiar-as-infraestruturas-de-ia/
https://www.portaldeangola.com/banco-mundial-e-banco-africano-de-desenvolvimento-unem-forcas-para-levar-eletricidade-a-300-milhoes-de-africanos-ate-2030/
https://www.portaldeangola.com/africa50-mobilizou-mais-de-us-55-mil-milhoes-em-financiamento-de-infraestruturas-criticas-em-todo-o-continente-disse-o-presidente-da-bad/
https://www.portaldeangola.com/onu-adota-pacto-que-busca-salvar-a-cooperacao-global-entre-paises/
https://www.portaldeangola.com/eleicoes-regionais-na-alemanha-sondagem-a-boca-das-urnas-da-vitoria-por-curta-margem-ao-spd/
https://www.portaldeangola.com/maputo-comunidades-preocupadas-com-baixo-nivel-de-condicoes-de-ensino/
https://www.portaldeangola.com/angola-e-cazaquistao-querem-estreitar-cooperacao/
https://www.portaldeangola.com/brasil-lidera-a-posicao-do-g-20-para-pressionar-a-reforma-das-instituicoes-de-governanca-global-a-onu-omc-fmi-e-wb/
https://www.portaldeangola.com/primeira-ministra-da-dinamarca-diz-que-a-ue-precisa-ser-dura-com-os-imigrantes/
https://www.portaldeangola.com/biden-diz-a-trump-que-os-migrantes-sao-o-sangue-dos-estados-unidos/
https://www.portaldeangola.com/brasil-nao-tem-planos-para-emissao-especifica-ligada-a-amazonia-foca-em-titulos-sustentaveis-diz-tesouro/
https://www.portaldeangola.com/ue-obtera-emprestimo-de-35-mil-milhoes-de-euros-para-a-ucrania-atraves-de-ativos-congelados-da-russia/
https://www.portaldeangola.com/zelensky-diz-que-espera-que-biden-apoie-o-seu-plano-para-acabar-com-a-guerra-com-a-russia/
https://www.portaldeangola.com/policia-detem-600-imigrantes-ilegais-na-lunda-norte/
https://www.portaldeangola.com/parlamento-europeu-reconhece-o-opositor-edmundo-gonzalez-como-presidente-da-venezuela/
https://www.portaldeangola.com/portugal-governo-avalia-retirar-bandeira-portuguesa-de-navio-com-material-de-uso-militar-para-israel/
https://www.portaldeangola.com/africa-ocidental-e-central-o-numero-de-pessoas-deslocadas-a-forca-duplicou-em-5-anos-segundo-a-onu/
https://www.portaldeangola.com/observatorio-da-maianga-ponto-previo-em-jeito-de-apresentacao/
https://www.portaldeangola.com/google-vence-disputa-judicial-de-15-mil-milhoes-de-euros-com-a-ue-por-abuso-de-posicao-dominante-nos-anuncios-da-adsense/
https://www.portaldeangola.com/fed-corta-taxas-de-juro-em-0-5-numa-tentativa-decisiva-de-preservar-a-forca-da-economia-dos-eua/
https://www.portaldeangola.com/jpmorgan-o-maior-banco-de-investimentos-privados-dos-eua-tenciona-expandir-as-suas-atividades-em-africa/
https://www.portaldeangola.com/forum-china-africa-2024-como-a-transicao-energetica-pode-alavancar-a-parceria-e-criar-uma-situacao-vantajosa-para-os-dois-lados/
https://www.portaldeangola.com/a-quadratura-do-circulo-angolano-chama-se-bicefalia/
https://www.portaldeangola.com/emprestimos-da-china-a-africa-aumentam-pela-primeira-vez-em-sete-anos-enquanto-angola-ocupa-o-primeiro-lugar-no-periodo-2000-2023/
https://www.portaldeangola.com/mercados-emergentes-globalizacao-e-o-paradoxo-de-lucas/
https://www.portaldeangola.com/o-presidente-dos-eua-joe-biden-fara-a-primeira-visita-a-africa-com-viagem-a-angola-nas-proximas-semanas-relata-a-reuters/
https://www.portaldeangola.com/a-capacidade-de-armazenamento-de-energia-e-atualmente-o-maior-obstaculo-a-expansao-das-energias-renovaveis-alerta-a-cop29/
https://www.portaldeangola.com/a-dependencia-de-angola-do-petroleo-deixa-pouco-espaco-para-o-servico-da-divida-enquanto-a-diversificacao-da-economia-leva-tempo/
https://www.portaldeangola.com/a-gigante-portuaria-dp-world-dos-eau-lanca-parceria-com-o-nedbank-da-africa-do-sul-para-financiar-o-comercio-de-pequenas-empresas/
https://www.portaldeangola.com/quenia-inicia-auditoria-da-divida-publica-para-garantir-mais-responsabilidade-e-transparencia-diz-ministro-das-financas/
https://www.portaldeangola.com/o-fabricante-de-automoveis-chines-byd-assume-o-controle-total-da-joint-venture-com-a-mercedes-benz-na-china/
https://www.portaldeangola.com/hildegarda-de-bingen-a-santa-que-descreveu-orgasmo-feminino-pela-1a-vez-e-inventou-formula-da-cerveja/
https://www.portaldeangola.com/spacex-vai-lancar-naves-espaciais-para-marte-em-2026-diz-elon-musk/
https://www.portaldeangola.com/mega-el-nino-levou-a-maior-extincao-em-massa-da-historia/
https://www.portaldeangola.com/a-rapida-implementacao-da-producao-de-energia-solar-e-eolica-na-europa-ultrapassou-a-capacidade-de-armazenamento-de-energia/
https://www.portaldeangola.com/quenia-lanca-parceria-publico-privada-de-13-mil-milhoes-de-dolares-para-construir-linhas-de-energia-de-alta-tensao/
https://www.portaldeangola.com/gana-aumenta-preco-do-cacau-em-45-para-melhorar-a-renda-dos-pequenos-agricultores-e-desencorajar-o-contrabando/
https://www.portaldeangola.com/novas-oportunidades-surgem-no-acesso-a-energia-em-meio-aos-desafios-na-africa-oriental-e-meridional-diz-a-comesa/
https://www.portaldeangola.com/a-tanzania-esta-a-impulsionar-a-sua-agenda-para-fortalecer-a-economia-digital/
https://www.portaldeangola.com/eua-apoiam-dois-assentos-permanentes-no-conselho-de-seguranca-da-onu-para-africa/
https://www.portaldeangola.com/banco-central-europeu-corta-novamente-as-taxas-de-juro-a-medida-que-a-inflacao-diminui-e-a-economia-abranda/
https://www.portaldeangola.com/quenia-proibe-importacoes-de-acucar-fora-dos-blocos-comerciais-da-comesa-e-da-eac/
https://www.portaldeangola.com/italia-questiona-proibicao-da-ue-sobre-motores-de-combustao-a-partir-de-2035-num-reves-para-o-acordo-verde-da-ue/
https://www.portaldeangola.com/saudi-aramco-expande-atividades-downstream-com-o-aumento-da-cooperacao-com-gigantes-petroquimicas-chinesas/
https://www.portaldeangola.com/primeiro-ministro-espanhol-pede-a-ue-que-reconsidere-as-tarifas-sobre-veiculos-eletricos-da-china/
https://www.portaldeangola.com/a-industria-automovel-um-dos-pilares-da-economia-alema-enfrenta-uma-das-maiores-crises-das-ultimas-decadas/
https://www.portaldeangola.com/diplomata-defende-apoio-politico-completo-e-consistente-as-operacoes-de-paz/
https://www.portaldeangola.com/porque-e-que-a-alemanha-esta-agora-a-reforcar-os-seus-controlos-fronteiricos/
https://www.portaldeangola.com/ue-fornece-financiamento-para-hidrogenio-verde-na-africa-do-sul/
https://www.portaldeangola.com/relatorio-draghi-sobre-o-futuro-da-competitividade-da-ue-diagnostico-economico-correcto-mas-financeiramente-inviavel/
https://www.portaldeangola.com/empresas-chinesas-assinam-acordo-com-a-namibia-para-contruir-a-maior-fabrica-solar/
https://www.portaldeangola.com/a-sustentabilidade-esta-a-sair-da-lista-de-prioridades-das-grandes-empresas-enquanto-os-consumidores-a-veem-como-prioridade/
https://www.portaldeangola.com/a-exxon-desiste-da-corrida-para-comprar-participacao-no-bloco-de-petroleo-da-namibia-da-galp/
https://www.portaldeangola.com/grandes-empresas-petroliferas-e-comerciantes-de-petroleo-competem-para-investir-em-actividades-downstream/
https://www.portaldeangola.com/bolsonaro-chama-moraes-de-ditador-durante-manifestacao-de-apoiadores-em-sao-paulo/
https://www.portaldeangola.com/aeronave-com-grande-quantidade-de-droga-apreendida-em-bissau/
https://www.portaldeangola.com/incendio-em-escola-do-quenia-mata-17-criancas/
https://www.portaldeangola.com/mpla-marcha-em-apoio-ao-pr-enquanto-ativistas-dizem-que-nao-podem-manifestar-se/
https://www.portaldeangola.com/dbsa-aprova-200-milhoes-de-dolares-para-o-projeto-ferroviario-do-corredor-do-lobito-em-angola/
https://www.portaldeangola.com/impulsionada-por-reformas-sob-o-governo-de-unidade-nacional-a-africa-do-sul-esta-a-mostrar-sinais-de-recuperacao/
https://www.portaldeangola.com/angola-procura-consolidar-lacos-com-washington-como-anfitria-da-cimeira-empresarial-eua-africa-de-2025/
https://www.portaldeangola.com/negociacoes-climaticas-entre-china-e-eua-serao-retomadas-esta-semana-em-pequim/
https://www.portaldeangola.com/petroleo-em-queda-livre-enquanto-as-preocupacoes-com-a-procura-superam-a-intencao-da-opep-de-restringir-oferta/
https://www.portaldeangola.com/focac-china-assina-acordo-com-a-zambia-e-a-tanzania-para-reabilitar-o-tazara-concorrente-do-corredor-do-lobito-em-angola/
https://www.portaldeangola.com/china-e-nigeria-anunciam-reforco-dos-lacos-economicos-durante-o-focac/
https://www.portaldeangola.com/china-destaca-a-solidariedade-com-o-sul-global-na-abertura-do-forum-de-cooperacao-africa-china-focac/
https://www.portaldeangola.com/tempestade-em-roma-raio-atinge-e-danifica-o-arco-de-constantino/
https://www.portaldeangola.com/indonesia-papa-francisco-apela-ao-reforco-do-dialogo-inter-religioso/
https://www.portaldeangola.com/entrou-em-vigor-o-primeiro-acordo-de-facilitacao-do-investimento-sustentavel-celebrado-com-angola/
https://www.portaldeangola.com/o-petroleo-cai-a-medida-que-o-aumento-da-oferta-e-a-demanda-morna-intensificam/
https://www.portaldeangola.com/eua-grandes-petroliferas-pedem-a-kamala-harris-que-seja-honesta-sobre-os-seus-planos-de-energia-e-clima/
https://www.portaldeangola.com/o-focac-e-a-cimeira-africa-mais-um-como-sair-da-armadilha-de-que-africa-e-apenas-um-pais/
https://www.portaldeangola.com/a-mega-refinaria-de-petroleo-de-dangote-da-nigeria-vai-comecar-a-produzir-gasolina/
https://www.portaldeangola.com/a-volkswagen-esta-a-considerar-encerrar-fabricas-na-alemanha-num-gesto-sem-precedentes/
https://www.portaldeangola.com/ha-erros-dos-dois-lados-que-estao-se-retroalimentando-avalia-professor-da-usp-sobre-embate-entre-moraes-e-musk/
https://www.portaldeangola.com/china-recebe-governantes-da-africa-para-reuniao-de-cimeira-de-cinco-dias/
https://www.portaldeangola.com/fundo-soberano-alcanca-resultados-historicos-de-usd-19935-milhoes/
https://www.portaldeangola.com/angola-e-o-maior-parceiro-economico-africano-da-china/
https://www.portaldeangola.com/angola-paga-fornecedores-locais-com-letras-do-tesouro-por-falta-de-liquidez/
https://www.portaldeangola.com/inflacao-alema-cai-para-2-abrindo-caminho-para-novo-corte-das-taxas-de-juro-por-parte-do-banco-central-europeu/
https://www.portaldeangola.com/kuleba-e-borrell-pedem-levantamento-das-restricoes-ao-uso-de-armas-ocidentais-contra-a-russia/
https://www.portaldeangola.com/openai-negoceia-ronda-de-financiamento-avaliando-a-acima-de-100-mil-milhoes-de-dolares/
https://www.portaldeangola.com/reino-unido-e-alemanha-visam-novo-pacto-de-cooperacao-enquanto-starmer-reconstroi-lacos-com-a-ue/
https://www.portaldeangola.com/a-importancia-das-energias-renovaveis-na-producao-de-eletricidade-nos-paises-do-g20/
https://www.portaldeangola.com/a-namibia-acelera-a-formulacao-de-politicas-de-conteudo-local-para-que-os-namibianos-beneficiem-do-petroleo-e-do-gas/
https://www.portaldeangola.com/credito-do-sector-nao-financeiro-cresce-68-bilioes-de-kwanzas-em-julho/
https://www.portaldeangola.com/chissema-aposta-na-descoberta-de-novas-reservas-de-diamantes/
https://www.portaldeangola.com/mais-de-40-da-electricidade-mundial-veio-de-energias-renovaveis-em-2023-mas-apenas-10-paises-contribuiram-com-75-do-esforco/
https://www.portaldeangola.com/lideres-africanos-deslocam-se-a-pequim-para-o-forum-de-cooperacao-africa-china-focac/
https://www.portaldeangola.com/o-canada-anunciou-tarifas-de-100-sobre-os-carros-eletricos-e-de-25-sobre-o-aco-e-o-aluminio-importados-da-china/
https://www.portaldeangola.com/petroleo-sobe-3-com-cortes-na-producao-da-libia-e-preocupacoes-com-o-conflito-no-medio-oriente/
https://www.portaldeangola.com/bmw-ultrapassa-tesla-e-lidera-o-ranking-de-vendas-de-veiculos-eletricos-da-europa-pela-primeira-vez/
https://www.portaldeangola.com/o-regulador-de-energia-da-zambia-rejeitou-aumento-de-156-no-preco-da-energia-a-medida-que-a-seca-aprofunda-os-cortes/
https://www.portaldeangola.com/precos-do-cobalto-e-do-litio-em-queda-dois-minerais-essenciais-para-a-transicao-energetica/
https://www.portaldeangola.com/estados-unidos-powell-diz-que-chegou-a-hora-do-fed-cortar-as-taxas-de-juros/
https://www.portaldeangola.com/maior-fabricante-mundial-de-turbinas-eolicas-declara-lucros-com-o-boom-das-energias-renovaveis-na-china/
https://www.portaldeangola.com/macron-inicia-consultas-na-franca-para-nomear-novo-governo/
https://www.portaldeangola.com/aeroportos-europeus-voltam-a-recorrer-a-modelos-raio-x-para-controlar-as-malas/
https://www.portaldeangola.com/nao-vamos-regredir-diz-kamala-harris-ao-encerrar-convencao-democrata/
https://www.portaldeangola.com/angola-e-china-abordam-cooperacao-bilateral/
https://www.portaldeangola.com/presos-por-narcotrafico-na-arabia-saudita-vivem-aflitos-a-espera-da-execucao/
https://www.portaldeangola.com/dirigentes-do-fed-estariam-propensos-a-cortar-juros-em-setembro/
https://www.portaldeangola.com/conversacoes-para-cessar-fogo-em-gaza-egito-diz-que-hamas-nao-vai-aceitar/
https://www.portaldeangola.com/mpox-angola-com-risco-elevado-devido-a-fronteira-com-rdc/
https://www.portaldeangola.com/quenia-lanca-campanha-para-destacar-as-oportunidades-do-acordo-de-parceria-economica-com-a-ue/
https://www.portaldeangola.com/agricultura-sustentavel-cientistas-reunem-se-no-quenia-para-promover-o-comercio-de-sementes-certificadas/
https://www.portaldeangola.com/bancos-centrais-divergem-no-caminho-das-taxas-de-juro-antes-da-reuniao-de-jackson-hole-nos-estados-unidos/
https://www.portaldeangola.com/a-comissao-europeia-divulgou-as-conclusoes-preliminares-sobre-a-investigacao-de-subsidios-de-veiculos-eletricos-da-china/
https://www.portaldeangola.com/o-gana-inicia-a-construcao-de-uma-refinaria-de-petroleo-no-meio-de-duvidas-sobre-a-viabilidade-comercial-do-projeto/
https://www.portaldeangola.com/petroleo-cai-enquanto-temores-sobre-a-demanda-na-china-reacendem-sentimento-pessimista-dos-mercados/
https://www.portaldeangola.com/os-principais-obstaculos-no-caminho-da-etiopia-para-a-reestruturacao-da-divida/
https://www.portaldeangola.com/china-e-eua-cooperam-para-reforcar-a-estabilidade-financeira-internacional-e-enfrentar-eventos-de-stress-financeiro/
https://www.portaldeangola.com/rd-congo-tera-em-breve-o-primeiro-porto-de-aguas-profundas-melhorando-o-acesso-do-pais-aos-mercados-internacionais/
https://www.portaldeangola.com/el-nino-e-alteracoes-climaticas-quase-68-milhoes-de-pessoas-sofrem-com-a-seca-na-africa-austral/
https://www.portaldeangola.com/standard-bank-devera-aumentar-participacao-em-negocios-na-nigeria-e-em-angola/
https://www.portaldeangola.com/o-brasil-vai-aderir-a-iniciativa-do-cinturao-e-rota-da-china/
https://www.portaldeangola.com/a-seca-induzida-pelo-el-nino-podera-obrigar-a-zambia-a-aumentar-as-tarifas-de-eletricidade-ate-156/
https://www.portaldeangola.com/numa-iniciativa-com-elevados-riscos-politicos-parlamento-sul-africano-vai-debater-aumento-do-preco-da-energia-da-eskom/
https://www.portaldeangola.com/nigeria-pretende-arrecadar-2-mil-milhoes-de-dolares-com-a-venda-de-obrigacoes-em-dolares-a-investidores-nacionais/
https://www.portaldeangola.com/netanyahu-pede-pressao-sobre-o-hamas-para-alcancar-tregua-antes-de-encontro-com-blinken/
https://www.portaldeangola.com/rei-da-tailandia-nomeia-paetongtarn-shinawatra-como-primeira-ministra/
https://www.portaldeangola.com/morte-de-alain-delon-o-ultimo-monstro-sagrado-do-cinema-frances/
https://www.portaldeangola.com/ouro-supera-us-25-mil-por-onca-e-bate-recorde-historico/
https://www.portaldeangola.com/venezuela-e-regime-com-vies-autoritario-mas-nao-ditadura-diz-lula/
https://www.portaldeangola.com/camera-de-comercio-anuncia-investimento-nigeriano-a-angola-de-usd-500-milhoes/
https://www.portaldeangola.com/pr-confirma-reuniao-em-luanda-sobre-paz-para-rdc-rwanda/
https://www.portaldeangola.com/ha-75-anos-alemanha-votava-pela-primeira-vez-apos-hitler/
https://www.portaldeangola.com/focac-2024-agenda-da-china-no-forum-africa-china-2024-clima-conectividade-global-e-alianca-politica-com-o-sul-global/
https://www.portaldeangola.com/eua-consideram-uma-medida-antitruste-rara-desmembrar-o-google/
https://www.portaldeangola.com/como-as-grandes-empresas-tecnologicas-tentam-reescrever-as-regras-sobre-emissoes-liquidas-zero-de-carbono/
https://www.portaldeangola.com/meta-minimiza-ameaca-da-ia-generativa-em-campanhas-e-eleicoes/
https://www.portaldeangola.com/o-museu-da-escravatura/
https://www.portaldeangola.com/tosyali-da-turquia-vai-construir-uma-fabrica-integrada-de-ferro-e-aco-em-angola/
https://www.portaldeangola.com/precos-do-petroleo-sob-pressao-apesar-da-incerteza-geopolitica-no-medio-oriente/
https://www.portaldeangola.com/inflacao-basica-dos-eua-diminui-pelo-quarto-mes-abrindo-o-caminho-para-um-corte-das-taxas-de-juro-do-fed/
https://www.portaldeangola.com/oms-considera-surto-de-variola-venerea-na-africa-uma-emergencia-sanitaria-global/
https://www.portaldeangola.com/repensar-os-objetivos-de-desenvolvimento-sustentavel/
https://www.portaldeangola.com/nova-tecnologia-de-perfuracao-offshore-de-ultra-alta-pressao-abre-novas-perspetivas-para-a-producao-de-petroleo-incluindo-em-angola/
https://www.portaldeangola.com/o-que-e-o-nativismo-que-esta-no-cerne-das-propostas-de-trump-e-da-direita-radical-na-europa/
https://www.portaldeangola.com/violencia-matou-mais-de-15-mil-jovens-no-brasil-em-tres-anos/
https://www.portaldeangola.com/presidente-versus-procuradora-geral-uma-luta-com-prognostico-reservado-na-guatemala/
https://www.portaldeangola.com/ucrania-anuncia-novos-avancos-em-territorio-russo/
https://www.portaldeangola.com/febre-do-litio-na-argentina-ofusca-preocupacao-ambiental/
https://www.portaldeangola.com/execucao-do-oge-2022-promove-estabilidade-macroeconomica/
https://www.portaldeangola.com/investidores-estrangeiros-retiram-quantia-recorde-de-dinheiro-da-china/
https://www.portaldeangola.com/a-euforia-pelo-hidrogenio-verde-comeca-a-arrefecer-por-falta-de-clientes-para-comprar-o-combustivel/
https://www.portaldeangola.com/opep-reduz-previsao-da-procura-de-petroleo-enquanto-os-precos-sobem-impulsionados-pela-crise-no-medio-oriente/
https://www.portaldeangola.com/4-formas-extremamente-raras-de-engravidar/
https://www.portaldeangola.com/licoes-da-refinaria-de-dangote-na-nigeria-para-as-aspiracoes-de-angola-e-outros-paises-africanos-de-acrescentar-valor-as-suas-materias-primas/
https://www.portaldeangola.com/industria-petrolifera-dos-eua-bombeia-volumes-recordes-a-medida-que-a-eficiencia-aumenta-e-os-custos-diminuem/
https://www.portaldeangola.com/procura-de-petroleo-abaixo-do-esperado-pode-forcar-a-opep-a-atrasar-flexibilizacao-de-cortes/
https://www.portaldeangola.com/etiopia-airlines-assina-acordo-para-o-projeto-do-maior-aeroporto-da-africa/
https://www.portaldeangola.com/paul-kagame-elogia-esforcos-do-pr-angolano-em-busca-da-paz/
https://www.portaldeangola.com/levantamento-de-dinheiro-em-tpa-atinge-record-de-mais-50-mil-dia/
https://www.portaldeangola.com/a-re-globalizacao-e-o-papel-de-africa-na-criacao-do-futuro-desenvolvimento-sustentavel/
https://www.portaldeangola.com/producao-de-petroleo-dos-estados-unidos-atinge-novo-recorde-em-agosto/
https://www.portaldeangola.com/a-china-vai-comecar-a-estabelecer-metas-rigorosas-para-reduzir-as-emissoes-de-carbono-e-acelerar-a-transicao-energetica/
https://www.portaldeangola.com/gana-abre-refinaria-para-se-tornar-um-centro-de-ouro-em-africa-e-aumentar-o-valor-acrescentado-dos-seus-minerios/
https://www.portaldeangola.com/emirados-arabes-unidos-suspendem-32-refinarias-de-ouro-em-repressao-a-lavagem-de-dinheiro/
https://www.portaldeangola.com/fbi-em-alerta-para-eventuais-ataques-a-convencao-democrata/
https://www.portaldeangola.com/dolcegabbana-lanca-perfume-para-caes-por-mais-de-us-100/
https://www.portaldeangola.com/bangladesh-nobel-da-paz-toma-posse-como-primeiro-ministro/
https://www.portaldeangola.com/no-caso-dividas-ocultas-chang-e-culpado-determinam-jurados/
https://www.portaldeangola.com/reacao-do-x-a-motins-no-reino-unido-pode-ter-impacto-na-investigacao-da-lei-digital-diz-comissao/
https://www.portaldeangola.com/suspeito-de-planear-ataques-a-concertos-de-taylor-swift-em-viena-jurou-lealdade-ao-estado-islamico/
https://www.portaldeangola.com/russia-enfrenta-terceiro-dia-de-incursao-ucraniana-em-regiao-fronteirica/
https://www.portaldeangola.com/glencore-recua-no-plano-de-sair-do-lucrativo-negocio-do-carvao-sob-pressao-dos-investidores/
https://www.portaldeangola.com/ate-a-suica-esta-a-discutir-como-taxar-os-super-ricos/
https://www.portaldeangola.com/a-etu-energias-de-angola-pretende-lancar-ipo-em-2026-apos-compra-de-participacao-na-galp-portuguesa/
https://www.portaldeangola.com/lobby-do-minerio-de-cobre-preocupado-com-a-proposta-de-lei-da-zambia-para-regular-o-sector/
https://www.portaldeangola.com/cerebro-dos-atentados-de-7-de-outubro-apontado-como-novo-lider-do-hamas/
https://www.portaldeangola.com/vendas-de-veiculos-eletricos-na-alemanha-caem-37-com-o-fim-dos-subsidios-acompanhando-a-desaceleracao-global-dos-ve/
https://www.portaldeangola.com/quenia-planeia-redirecionar-o-perfil-da-divida-para-emprestimos-multilaterais-em-condicoes-favoraveis/
https://www.portaldeangola.com/banco-mundial-aconselha-camaroes-a-arrecadar-mais-impostos-e-gastar-melhor/
https://www.portaldeangola.com/nigeria-detem-manifestantes-com-bandeiras-russas-enquanto-protestos-contra-as-reformas-economicas-entram-no-sexto-dia/
https://www.portaldeangola.com/kamala-harris-escolhe-tim-walz-como-candidato-a-vice-presidente-dizem-fontes/
https://www.portaldeangola.com/bolsas-se-recuperam-apos-segunda-feira-turbulenta/
https://www.portaldeangola.com/mercados-financeiros-caem-a-pique-com-perdas-de-us-64-trilhoes-o-equivalente-ao-dobro-do-pib-do-continente-africano/
https://www.portaldeangola.com/o-que-podem-angola-e-outros-paises-africanos-esperar-do-forum-de-cooperacao-africa-china-2024/
https://www.portaldeangola.com/bolsa-de-toquio-desaba-124-e-registra-a-maior-queda-em-pontos-na-historia/
https://www.portaldeangola.com/despedida-chocante-filmes-e-series-abandonam-netflix-em-agosto-2024/
https://www.portaldeangola.com/ao-menos-50-mortos-em-protestos-contra-o-governo-em-bangladesh/
https://www.portaldeangola.com/zelensky-agora-e-a-realidade-os-f-16-estao-na-ucrania/
https://www.portaldeangola.com/angola-apresenta-solucoes-para-desenvolvimento-de-infra-estruturas-em-africa/
https://www.portaldeangola.com/pacote-basico-de-televisao-esta-isento-da-actualizacao-de-precos/
https://www.portaldeangola.com/kamala-e-trump-tem-desacordo-sobre-data-do-debate-presidencial/
https://www.portaldeangola.com/por-que-kim-jong-un-quer-trump-de-volta-a-presidencia-dos-eua-segundo-desertor/
https://www.portaldeangola.com/disputa-da-lideranca-do-mpla/
https://www.portaldeangola.com/salarios-da-funcao-publica-pagos-na-totalidade/
https://www.portaldeangola.com/ministro-eugenio-laborinho-garante-aumento-dos-niveis-do-policiamento-de-proximidade/
https://www.portaldeangola.com/quem-sera-o-vice-de-kamala-harris-na-corrida-a-casa-branca/
https://www.portaldeangola.com/atentado-islamista-em-praia-da-somalia-deixa-mais-de-30-mortos/
https://www.portaldeangola.com/trump-aceita-debate-com-kamala-harris-na-fox-news-em-4-de-setembro/
https://www.portaldeangola.com/china-fornece-novos-detalhes-sobre-a-proxima-cimeira-com-a-africa-enquanto-os-eua-manifestam-preocupacao/
https://www.portaldeangola.com/quenia-tribunal-anula-lei-de-financas-de-2023-em-novo-golpe-para-o-presidente-ruto/
https://www.portaldeangola.com/eua-ponderam-aumentar-as-restricoes-ao-acesso-da-china-a-chips-de-memoria-de-ia/
https://www.portaldeangola.com/africa-caminha-para-mais-uma-guerra-mortifera-no-congo-alimentada-pela-corrida-aos-minerais-essenciais-para-a-transicao-energetica/
https://www.portaldeangola.com/estados-unidos-fed-abre-caminho-para-corte-das-taxas-de-juro-em-setembro/
https://www.portaldeangola.com/lider-do-hamas-e-morto-no-irao/
https://www.portaldeangola.com/angola-empata-com-hungria-nos-jogos-olimpicos/
https://www.portaldeangola.com/oposicao-se-mobiliza-na-venezuela-apos-protestos-que-deixaram-pelo-menos-12-mortos/
https://www.portaldeangola.com/cessar-fogo-na-republica-democratica-do-congo-apos-conversacoes-mediadas-por-angola/
https://www.portaldeangola.com/israel-realiza-bombardeio-seletivo-em-suburbio-de-beirute-contra-comandante-do-hezbollah/
https://www.portaldeangola.com/kamala-mantem-vantagem-de-1-ponto-sobre-trump-em-nova-pesquisa-reuters-ipsos/
https://www.portaldeangola.com/elon-musk-e-criticado-por-compartilhar-deepfake-de-kamala-harris/
https://www.portaldeangola.com/trump-aceita-ser-ouvido-como-vitima-pelo-fbi-apos-fracassada-tentativa-de-assassinato/
https://www.portaldeangola.com/a-primeira-ministra-italiana-meloni-assume-papel-de-mediadora-nas-relacoes-entre-ue-e-a-china-irritando-com-isso-bruxelas/
https://www.portaldeangola.com/petroleo-brent-cai-abaixo-de-us-80-o-barril-pela-primeira-vez-desde-junho/
https://www.portaldeangola.com/nigerianos-fazem-fila-para-o-combustivel-obrigando-o-governo-a-entrar-em-acordo-com-a-refinaria-de-dangote/
https://www.portaldeangola.com/jo-2024-angola-venceu-a-espanha-no-andebol-feminino/
https://www.portaldeangola.com/governo-lanca-campanha-de-rastreio-do-cancro-da-prostata/
https://www.portaldeangola.com/ministros-do-g20-comprometem-se-a-reduzir-as-desigualdades-globais/
https://www.portaldeangola.com/ue-da-formalmente-inicio-a-procedimentos-relativos-ao-defice-excessivo-contra-varios-estados-membros/
https://www.portaldeangola.com/precos-do-cafe-disparam-nos-mercados-internacionais/
https://www.portaldeangola.com/secretaria-do-tesouro-dos-eua-yellen-chama-a-luta-pelo-clima-de-a-maior-oportunidade-economica-global/
https://www.portaldeangola.com/primeira-ministra-da-italia-giorgia-meloni-promete-relancamento-dos-lacos-com-pequim-na-sua-visita-oficial-a-china/
https://www.portaldeangola.com/um-mundo-de-baixo-crescimento-e-um-mundo-desigual-e-instavel-diretora-geral-do-fmi-na-reuniao-do-g20/
https://www.portaldeangola.com/nao-devemos-matar-as-industrias-locais-presidente-do-bad-apoia-a-refinaria-de-dangote-contra-o-governo-da-nigeria/
https://www.portaldeangola.com/banco-central-da-china-volta-a-baixar-as-taxas-de-juros-numa-tentativa-para-relancar-a-economia/
https://www.portaldeangola.com/a-principal-categoria-de-fundos-esg-da-ue-sofre-saidas-recordes/
https://www.portaldeangola.com/a-economia-dos-eua-cresceu-mais-rapido-do-que-o-esperado-no-ultimo-trimestre-devido-a-demanda-firme/
https://www.portaldeangola.com/angola-nunca-levantara-a-questao-das-reparacoes-historicas-afirmou-o-presidente-da-republica-durante-a-visita-do-primeiro-ministro-portugues/
https://www.portaldeangola.com/africa-fusao-dos-mercados-da-eac-comesa-e-sadc-comeca-quinta-feira/
https://www.portaldeangola.com/eua-onde-kamala-harris-se-posiciona-em-relacao-as-alteracoes-climaticas-e-porque-e-que-isto-a-torna-vulneravel-aos-ataques-de-trump/
https://www.portaldeangola.com/china-surpreende-os-mercados-financeiros-com-cortes-em-varias-taxas-de-juros-para-apoiar-a-economia-fragil/
https://www.portaldeangola.com/refinaria-de-dangote-da-nigeria-em-negociacoes-com-a-libia-para-garantir-petroleo-e-interessada-no-petroleo-de-angola/
https://www.portaldeangola.com/o-petroleo-cai-enquanto-os-mercados-desvalorizam-a-saida-de-biden-e-se-concentram-nos-fundamentos-da-procura-e-oferta/
https://www.portaldeangola.com/trump-diz-que-kamala-harris-sera-mais-facil-de-derrotar-do-que-biden/
https://www.portaldeangola.com/presidente-joao-lourenco-em-accra-para-reuniao-da-uniao-africana/
https://www.portaldeangola.com/militantes-estrangeiros-sao-agredidos-e-feridos-por-colonos-na-cisjordania-ocupada/
https://www.portaldeangola.com/tensoes-e-ataques-entre-israel-huthis-do-iemen-e-hezbollah-do-libano/
https://www.portaldeangola.com/com-kamala-harris-democratas-estariam-apostando-contra-historia-de-sexismo-e-racismo-dos-eua/
https://www.portaldeangola.com/joe-biden-desiste-da-corrida-a-casa-branca/
https://www.portaldeangola.com/comicio-republicano-trump-diz-que-levou-tiro-pela-democracia-e-elogia-putin-xi-e-orban/
https://www.portaldeangola.com/movimento-mudei-admite-impugnar-lei-do-vandalismo-em-angola/
https://www.portaldeangola.com/manifestantes-anti-corrupcao-do-uganda-prometem-desafiar-a-proibicao-da-policia/
https://www.portaldeangola.com/pr-aponta-entraves-a-integracao-continental/
https://www.portaldeangola.com/apagao-global-afeta-companhias-aereas-bancos-e-hospitais/
https://www.portaldeangola.com/biden-planeja-volta-a-campanha-e-democratas-se-reunem-sobre-processo-de-indicacao/
https://www.portaldeangola.com/zelensky-concordou-encontrar-se-pessoalmente-com-trump-para-discutir-a-paz/
https://www.portaldeangola.com/eua-e-angola-em-ofensiva-pela-paz-na-republica-democratica-do-congo/
https://www.portaldeangola.com/donald-trump-provoca-polemica-sobre-taiwan/
https://www.portaldeangola.com/novo-chefe-do-governo-britanico-recebe-a-europa-para-falar-de-seguranca-e-imigracao/
https://www.portaldeangola.com/taxas-de-juro-lagarde-diz-que-todas-as-opcoes-estao-em-aberto-para-setembro/
https://www.portaldeangola.com/por-que-e-importante-escolas-oferecerem-educacao-financeira/
https://www.portaldeangola.com/projecto-de-aceleracao-da-economia-desembolsa-usd-50-milhoes/
https://www.portaldeangola.com/ursula-von-der-leyen-reeleita-presidente-da-comissao-europeia-por-larga-maioria/
https://www.portaldeangola.com/biden-testa-positivo-para-covid-19-em-meio-a-disputa-politica-por-sua-candidatura/
https://www.portaldeangola.com/candidato-a-vice-de-trump-defende-trabalhadores-e-faz-alerta-a-aliados-dos-estados-unidos/
https://www.portaldeangola.com/responsabilizacao-criminal-de-atos-politicos/
https://www.portaldeangola.com/ex-pgr-lamenta-escutas-de-quatro-anos-a-joao-galamba-a-atual-pgr-acha-normal-e-admite-ate-mais-tempo/
https://www.portaldeangola.com/producao-interna-vai-ajudar-aliviar-inflacao-jose-de-lima-massano/
https://www.portaldeangola.com/projeto-2025-o-programa-ultraconservador-que-promete-uma-revolucao-nos-eua/
https://www.portaldeangola.com/governo-trabalhista-britanico-promete-melhorar-relacoes-com-parceiros-europeus/
https://www.portaldeangola.com/sistema-de-justica-em-angola-esta-muito-aquem-da-independencia-diz-bastonario-dos-advogados/
https://www.portaldeangola.com/an-e-grupo-de-mulheres-da-rdc-abordam-situacao-politica-e-social/
https://www.portaldeangola.com/sem-outra-escolha-o-presidente-frances-macron-aceita-demissao-do-primeiro-ministro-gabriel-attal/
https://www.portaldeangola.com/momento-critico-entre-a-oferta-e-a-procura-no-mercado-petrolifero/
https://www.portaldeangola.com/fmi-crescimento-global-estavel-em-meio-a-desinflacao-mais-lenta-e-a-crescente-fragmentacao-geoeconomica/
https://www.portaldeangola.com/com-a-escolha-do-vice-presidente-trump-prepara-se-para-uma-viragem-radical-na-politica-externa-dos-eua/
https://www.portaldeangola.com/estados-membros-da-ue-estao-de-acordo-com-imposicao-de-tarifas-provisorias-sobre-veiculos-eletricos-chineses/
https://www.portaldeangola.com/pr-exprime-solidariedade-para-com-as-vitimas-de-acidente-no-bie/
https://www.portaldeangola.com/o-crescimento-economico-da-china-e-pior-do-que-o-esperado-aumentando-a-pressao-sobre-xi/
https://www.portaldeangola.com/mais-de-12-empresas-petroliferas-demonstram-interesse-na-descoberta-de-petroleo-na-namibia/
https://www.portaldeangola.com/chegou-a-altura-de-verificar-a-realidade-economica-da-arabia-saudita/
https://www.portaldeangola.com/africa-do-sul-arrecadara-us-24-bilhoes-com-o-pacto-climatico-este-ano/
https://www.portaldeangola.com/donald-trump-escolhe-senador-j-d-vance-para-candidato-a-vice-presidente/
https://www.portaldeangola.com/trump-e-retirado-de-comicio-na-pensilvania-apos-disparos/
https://www.portaldeangola.com/as-negociacoes-no-mercado-cambial-da-russia-agora-sao-quase-100-em-yuan-chines/
https://www.portaldeangola.com/mercados-emergentes-mostram-resiliencia-apesar-do-aperto-monetario-global-diz-o-fmi/
https://www.portaldeangola.com/a-situacao-fiscal-no-quenia-devera-se-deteriorar-enquanto-os-manifestantes-prometem-continuar-os-protestos-na-proxima-semana/
https://www.portaldeangola.com/o-que-explica-o-excedente-comercial-historico-da-china-vantagens-comparativas-ou-subsidios/
https://www.portaldeangola.com/uma-biofabrica-de-mosquitos-na-colombia-luta-contra-a-dengue-e-a-desinformacao/
https://www.portaldeangola.com/franca-presidente-pede-a-forcas-republicanas-uma-maioria-solida/
https://www.portaldeangola.com/aliados-da-nato-iniciam-transferencia-de-jactos-f-16-para-a-ucrania/
https://www.portaldeangola.com/biden-vs-trump-quem-quer-que-joe-biden-seja-substituido/
https://www.portaldeangola.com/investidores-assinam-contratos-avaliados-em-mais-de-usd-300-milhoes/
https://www.portaldeangola.com/fed-avalia-ajuste-de-regra-que-pode-gerar-economia-de-bilhoes-em-capital-para-maiores-bancos-dos-eua-dizem-fontes/
https://www.portaldeangola.com/primeiro-ministro-da-india-critica-invasao-russa-a-ucrania-durante-encontro-com-putin/
https://www.portaldeangola.com/taag-renova-identidade-visual-das-aeronaves/
https://www.portaldeangola.com/primeira-dama-da-republica-participa-na-academia-global-anual/
https://www.portaldeangola.com/camaroes-filha-do-presidente-biya-torna-publica-a-sua-homossexualidade/
https://www.portaldeangola.com/supremo-de-angola-confirma-condenacoes-no-caso-500-milhoes/
https://www.portaldeangola.com/ios-18-traz-novo-fundo-dinamico-com-mudanca-de-cores-para-o-iphone/
https://www.portaldeangola.com/boeing-confessa-conspiracao-para-enganar-o-governo-dos-eua/
https://www.portaldeangola.com/a-inteligencia-artificial-ameaca-os-compromissos-climaticos-de-grandes-empresas-de-tecnologia/
https://www.portaldeangola.com/sera-que-a-opep-conseguira-controlar-a-producao-petrolifera-dos-seus-membros/
https://www.portaldeangola.com/dividas-publicas-esmagadoras-aguardam-os-novos-governos-na-europa-e-nos-estados-unidos/
https://www.portaldeangola.com/ataque-russo-com-misseis-deixa-36-mortos-e-atinge-hospital-infantil-diz-ucrania/
https://www.portaldeangola.com/tropas-ruandesas-combateram-ao-lado-dos-rebeldes-m23-na-rdc-afirmam-peritos-da-onu/
https://www.portaldeangola.com/presidente-queniano-propoe-cortes-orcamentais-apos-protestos-em-todo-o-pais-contra-o-aumento-de-impostos/
https://www.portaldeangola.com/franca-a-vitoria-da-esquerda-a-derrota-da-extrema-direita-e-a-incerteza-do-campo-macron/
https://www.portaldeangola.com/democratas-proeminentes-do-congresso-dos-eua-pedem-a-biden-que-abandone-a-corrida-presidencial-de-2024/
https://www.portaldeangola.com/cedeao-diz-que-corre-o-risco-de-desintegracao-se-o-burkina-faso-mali-e-niger-sairem-da-organizacao/
https://www.portaldeangola.com/mais-investimento-no-desenvolvimento-de-capital-humano-e-essencial-para-o-potencial-de-crescimento-de-africa-diz-ocde/
https://www.portaldeangola.com/cibercrime-se-reorganiza-diante-de-investidas-policiais/
https://www.portaldeangola.com/na-terra-natal-de-chavez-milhares-de-opositores-venezuelanos-pedem-mudanca/
https://www.portaldeangola.com/cabinda-ganha-novo-centro-prisional-com-infra-estruturas-de-formacao-academica/
https://www.portaldeangola.com/masoud-pezeshkian-vence-as-eleicoes-presidenciais-no-irao/
https://www.portaldeangola.com/novo-primeiro-ministro-britanico-diz-que-plano-de-deportacao-do-ruanda-esta-morto-e-enterrado/
https://www.portaldeangola.com/biden-diz-em-entrevista-que-se-sentia-mal-durante-debate-com-trump/
https://www.portaldeangola.com/o-que-se-segue-apos-a-vitoria-esmagadora-dos-trabalhistas-nas-eleicoes-britanicas/
https://www.portaldeangola.com/governo-anuncia-criacao-da-agencia-de-turismo-em-angola/
https://www.portaldeangola.com/fp-sadc-regista-progressos-na-transformacao-do-orgao-em-parlamento/
https://www.portaldeangola.com/projeto-2025-o-detalhado-plano-para-trump-mudar-os-eua-que-mobiliza-democratas/
https://www.portaldeangola.com/viktor-orban-ja-esta-na-russia-para-se-encontrar-com-vladimir-putin/
https://www.portaldeangola.com/fmi-diz-que-banco-nacional-de-angola-deve-preparar-liquidacao-de-bancos-problematicos/
https://www.portaldeangola.com/brasil-bolsonaro-acusado-de-novos-crimes/
https://www.portaldeangola.com/ue-adota-tarifas-adicionais-de-ate-38-sobre-veiculos-eletricos-chineses/
https://www.portaldeangola.com/archer-mangueira-o-governador-escritor-quer-mais-contribuicoes-da-geracao-da-transicao-para-a-historia-de-angola/
https://www.portaldeangola.com/mulher-de-36-anos-devorada-por-giboia-na-indonesia/
https://www.portaldeangola.com/partido-trabalhista-vence-eleicoes-no-reino-unido-com-maioria-absoluta/
https://www.portaldeangola.com/25-soldados-condenados-a-morte-por-fugir-do-inimigo-na-republica-democratica-do-congo/
https://www.portaldeangola.com/autoridades-desmentem-caso-de-variola-do-macaco-no-dundo/
https://www.portaldeangola.com/emirados-arabes-unidos-querem-criar-um-silicon-valley-para-a-inovacao-e-financiamento-climatico/
https://www.portaldeangola.com/r-d-congo-gecamines-aperta-controle-sobre-os-recursos-minerais-do-pais/
https://www.portaldeangola.com/nigeria-declara-emergencia-no-setor-petrolifero-em-meio-a-esforcos-para-aumentar-a-producao/
https://www.portaldeangola.com/kamala-harris-e-principal-opcao-para-substituir-biden-na-corrida-eleitoral-se-ele-se-afastar-dizem-fontes/
https://www.portaldeangola.com/dividas-ocultas-acordo-extrajudicial-protege-a-frelimo/
https://www.portaldeangola.com/cofco-ve-potencial-alta-em-safras-de-graos-do-brasil-em-24-25-enquanto-eleva-capacidade/
https://www.portaldeangola.com/eleicoes-francesas-mais-de-200-candidatos-desistem-da-segunda-volta/
https://www.portaldeangola.com/renamo-acusa-marcelo-de-envolvimento-na-pre-campanha/
https://www.portaldeangola.com/capacidades-fisicas-e-mentais-tramam-biden-e-nem-a-maioria-dos-democratas-o-quer/
https://www.portaldeangola.com/sadc-elogia-progresso-economico-de-angola/
https://www.portaldeangola.com/milei-chama-lula-de-perfeito-dinossauro-idiota-em-novo-ataque/
https://www.portaldeangola.com/dez-milhoes-de-luandenses-terao-agua-canalizada-ate-2027/
https://www.portaldeangola.com/sao-tome-acolhe-conferencia-sobre-mudancas-inconstitucionais-na-africa-central/
https://www.portaldeangola.com/leak-galaxy-s25-ultra-podera-ter-ecra-com-molduras-curvas/
https://www.portaldeangola.com/confira-como-serao-a-eleicao-e-o-funcionamento-da-camara-dos-comuns-do-reino-unido/
https://www.portaldeangola.com/ministerio-da-saude-reactiva-plano-de-contingencia-para-impedir-variola-do-macaco/
https://www.portaldeangola.com/pr-felicita-rdc-pelo-64-o-aniversario-da-independencia/
https://www.portaldeangola.com/justica-espanhola-recusa-conceder-amnistia-a-puigdemont-e-mantem-seu-mandado-de-prisao/
https://www.portaldeangola.com/steve-bannon-diz-que-vai-mobilizar-exercito-pro-trump-de-dentro-ou-fora-da-prisao/
https://www.portaldeangola.com/a-ultima-cartada-de-macron-para-tentar-impedir-que-direita-radical-controle-parlamento-na-franca/
https://www.portaldeangola.com/mirex-destaca-importancia-da-captacao-de-investimento-estrangeiro/
https://www.portaldeangola.com/franca-primeiras-estimativas-dao-vitoria-ao-partido-frente-nacional/
https://www.portaldeangola.com/charlotte-a-primeira-rainha-da-inglaterra-descendente-de-africanos/
https://www.portaldeangola.com/latinos-na-franca-temem-vitoria-da-extrema-direita/
https://www.portaldeangola.com/rebeldes-do-m23-apoiados-pelo-ruanda-tomam-cidade-chave-no-leste-da-rdc/
https://www.portaldeangola.com/ministra-de-estado-destaca-engajamento-da-igreja-na-promocao-da-paz/
https://www.portaldeangola.com/ymca-os-180-anos-de-associacao-crista-que-ganhou-nobel-da-paz-virou-hit-musical-e-inventou-o-volei/
https://www.portaldeangola.com/todos-os-28-arguidos-do-processo-de-fraude-fiscal-panama-papers-foram-absolvidos/
https://www.portaldeangola.com/funcao-publica-ja-beneficia-de-salario-superior-a-100-mil-kwanzas/
https://www.portaldeangola.com/panama-e-eua-firmarao-convenio-para-repatriar-migrantes-que-cruzarem-o-darien/
https://www.portaldeangola.com/ex-ceo-da-americanas-gutierrez-e-preso-em-madri-em-investigacao-sobre-fraude-bilionaria/
https://www.portaldeangola.com/biden-diz-que-se-mantem-na-corrida-a-presidencia/
https://www.portaldeangola.com/joao-lourenco-quer-sentar-tshisekedi-e-kagame-a-mesa-de-negociacoes/
https://www.portaldeangola.com/uniao-da-esquerda-pode-prejudicar-macron-e-dar-vitoria-a-direita-radical-nas-eleicoes-na-franca/
https://www.portaldeangola.com/catolicismo-em-declinio-irreversivel-na-alemanha/
https://www.portaldeangola.com/pr-felicita-antonio-costa-pela-eleicao-a-lideranca-do-conselho-europeu/
https://www.portaldeangola.com/recuros-naturais-de-angola-atraem-turistas-sul-africanos/
https://www.portaldeangola.com/a-reviravolta-fiscal-no-quenia-realca-a-dura-realidade-politica-do-elevado-peso-da-divida-publica-em-africa/
https://www.portaldeangola.com/como-e-que-o-gana-entrou-numa-crise-de-divida-e-foi-obrigado-a-procurar-um-resgate/
https://www.portaldeangola.com/ue-deve-adiar-regulamentacao-da-desflorestacao-diz-parlamentar-europeu-fazendo-eco-das-preocupacoes-dos-paises-em-desenvolvimento/
https://www.portaldeangola.com/antonio-costa-e-o-novo-presidente-do-conselho-europeu/
https://www.portaldeangola.com/com-alta-dos-precos-setor-do-azeite-busca-solucoes-para-crise-climatica/
https://www.portaldeangola.com/missao-lunar-chinesa-desencadeia-onda-de-desinformacao-contra-eua/
https://www.portaldeangola.com/presidente-da-bolivia-denuncia-tentativa-de-golpe-de-estado-militares-invadiram-sede-do-governo/
https://www.portaldeangola.com/meloni-contesta-negociacoes-antidemocraticas-para-cargos-de-topo-da-ue-e-pondera-abstencao/
https://www.portaldeangola.com/crencas-tradicionais-levam-a-discriminacao-contra-mulheres-sem-filhos/
https://www.portaldeangola.com/conflito-de-terra-leva-tenente-coronel-das-forcas-armadas-angolanas-a-prisao/
https://www.portaldeangola.com/vestidos-estrelam-maior-leilao-de-objetos-da-princesa-diana-em-quase-30-anos/
https://www.portaldeangola.com/assange-e-declarado-um-homem-livre-apos-acordo-de-admissao-de-culpa-com-justica-dos-eua/
https://www.portaldeangola.com/mark-rutte-nomeado-secretario-geral-da-nato/
https://www.portaldeangola.com/tpi-emite-mandados-de-prisao-contra-comandante-do-estado-maior-e-ex-ministro-russo/
https://www.portaldeangola.com/nome-de-antonio-costa-consegue-consenso-para-o-conselho-europeu/
https://www.portaldeangola.com/protestos-no-quenia-aumentam-de-intensidade-ha-mortos-e-muita-preocupacao-de-governos-ocidentais/
https://www.portaldeangola.com/biden-e-trump-se-enfrentam-em-primeiro-debate-na-quinta-feira/
https://www.portaldeangola.com/o-vestuario-politico-frances-analisado-por-especialistas/
https://www.portaldeangola.com/costa-do-marfim-namibia-e-africa-do-sul-estao-na-mira-das-grandes-petroliferas-a-medida-que-a-exploracao-offshore-se-intensifica/
https://www.portaldeangola.com/china-e-uniao-europeia-concordam-em-manter-negociacoes-sobre-tarifas-de-veiculos-eletricos/
https://www.portaldeangola.com/os-mercados-de-petroleo-caminham-para-um-excedente-ate-2030-embora-a-procura-continue-forte-nos-paises-emergentes-diz-a-aie/
https://www.portaldeangola.com/extrema-direita-avanca-como-favorita-nas-eleicoes-legislativas-da-franca/
https://www.portaldeangola.com/novo-governo-da-africa-do-sul-reaviva-tensoes-raciais/
https://www.portaldeangola.com/angola-mpla-anuncia-congresso-extraordinario-do-partido-em-dezembro-de-2024/
https://www.portaldeangola.com/tribunal-supremo-da-namibia-anula-lei-que-proibia-sexo-entre-homens/
https://www.portaldeangola.com/pedofilia-e-prostituicao-o-lado-obscuro-do-turismo-em-medellin/
https://www.portaldeangola.com/ue-iniciara-negociacoes-de-adesao-com-ucrania-e-moldavia-na-terca-feira/
https://www.portaldeangola.com/primeiro-ministro-portugues-visita-angola-em-julho/
https://www.portaldeangola.com/angola-comissao-economica-aprecia-proposta-de-novo-regime-de-precos-e-analisa-desempenho-economico-em-2024/
https://www.portaldeangola.com/dominio-do-dolar-no-sistema-de-reserva-internacional-continua-a-ceder-terreno-diz-o-fmi/
https://www.portaldeangola.com/empresa-chinesa-vai-executar-projectos-para-a-expansao-do-sistema-electrico-em-angola/
https://www.portaldeangola.com/china-usa-energia-nuclear-para-abastecer-a-industria-petroquimica-uma-inovacao-mundial/
https://www.portaldeangola.com/investimento-em-energia-limpa-devera-ser-o-dobro-dos-combustiveis-fosseis-em-2024-diz-a-aie/
https://www.portaldeangola.com/mark-rutte-se-aproxima-do-cargo-de-secretario-geral-da-otan/
https://www.portaldeangola.com/nova-viagem-nova-polemica-milei-volta-a-espanha-sem-se-encontrar-com-o-governo-nem-com-o-rei/
https://www.portaldeangola.com/multinacionais-ocidentais-que-fogem-da-nigeria-estao-a-ser-substituidas-por-empresas-asiaticas-e-turcas/
https://www.portaldeangola.com/eua-absorveram-33-dos-fluxos-de-investimento-globais-desde-a-covid-em-detrimento-dos-paises-emergentes/
https://www.portaldeangola.com/as-financas-publicas-dos-paises-da-zona-euro-representam-um-grande-risco-alerta-o-bce/
https://www.portaldeangola.com/eua-apoiam-angola-no-processamento-de-minerais-essenciais-e-exportacao-de-energia-disse-o-secretario-de-estado-adjunto/
https://www.portaldeangola.com/angola-anpg-quer-aumentar-a-producao-e-expandir-os-biocombustiveis-para-acelerar-a-transicao-energetica/
https://www.portaldeangola.com/nvidia-torna-se-empresa-mais-valiosa-da-bolsa-do-mundo/
https://www.portaldeangola.com/lula-acusa-campos-neto-de-trabalhar-para-prejudicar-o-pais-defende-sucessor-imune/
https://www.portaldeangola.com/euro2024-portugal-sofre-mas-vence-chequia-no-fim/
https://www.portaldeangola.com/na-celebracao-dos-40-anos-da-usaid-estados-unidos-reafirmam-apoio-a-mocambique/
https://www.portaldeangola.com/sonangol-e-chevron-assinam-contratos-para-exploracao-petrolifera-no-baixo-congo/
https://www.portaldeangola.com/ministerio-do-turismo-desafia-empresariado-a-investir-no-bico-de-angola/
https://www.portaldeangola.com/o-politico-de-direita-radical-de-28-anos-que-pode-se-tornar-primeiro-ministro-da-franca/
https://www.portaldeangola.com/sobe-para-sete-o-numero-de-mortos-pelas-intensas-chuvas-no-equador/
https://www.portaldeangola.com/angola-perspectiva-recuperar-parte-dos-767-pocos-petroliferos-inactivos/
https://www.portaldeangola.com/pr-assiste-investidura-de-cyril-ramaphosa/
https://www.portaldeangola.com/forcas-russas-resgatam-funcionarios-de-um-centro-de-detencao-e-matam-os-sequestradores/
https://www.portaldeangola.com/o-que-mulheres-da-antiguidade-pensavam-sobre-sexo-deveriam-se-livrar-da-vergonha-junto-com-as-roupas/
https://www.portaldeangola.com/franceses-marcham-em-massa-contra-avanco-da-extrema-direita/
https://www.portaldeangola.com/seguranca-maxima-na-suica-na-conferencia-de-paz-para-a-ucrania/
https://www.portaldeangola.com/aumento-dos-ataques-rebeldes-provoca-protestos-mortais-no-leste-do-congo/
https://www.portaldeangola.com/paises-se-reunem-na-suica-para-debater-paz-na-ucrania/
https://www.portaldeangola.com/numero-de-falencias-na-alemanha-dispara/
https://www.portaldeangola.com/nato-apresenta-estrategia-de-defesa-nao-vista-desde-a-guerra-fria/
https://www.portaldeangola.com/angotic-2024-universitarios-beneficiam-de-curso-sobre-tecnologia-espacial/
https://www.portaldeangola.com/pr-elogia-nivel-de-organizacao-do-secretariado-da-sadc/
https://www.portaldeangola.com/marcas-de-perfumes-de-luxo-estao-envolvidas-com-trabalho-infantil-revela-investigacao-da-bbc/
https://www.portaldeangola.com/fmi-aprova-desembolso-de-us-800-milhoes-para-argentina/
https://www.portaldeangola.com/tribunal-da-ue-decide-contra-fifa-e-uefa-no-caso-da-superliga/
https://www.portaldeangola.com/ensaio-clinico-com-novo-medicamento-indica-cura-em-100-de-doentes-oncologicos/
https://www.portaldeangola.com/standard-bank-vai-avancar-com-financiamento-do-oleoduto-do-uganda-de-5-mil-milhoes-de-dolares/
https://www.portaldeangola.com/opep-critica-aie-por-previsao-perigosa-do-pico-da-procura-de-petroleo-ate-2030/
https://www.portaldeangola.com/cimeira-do-g7-reforca-pgii-e-italia-anuncia-contribuicao-de-320-milhoes-de-dolares-para-o-corredor-do-lobito-em-angola/
https://www.portaldeangola.com/esperanca-da-costa-reitera-convite-ao-papa-para-visitar-angola/
https://www.portaldeangola.com/g7-fecha-acordo-de-us50-bilhoes-para-apoiar-a-ucrania/
https://www.portaldeangola.com/angotic-2024-huawei-apresenta-solucoes-para-provedores-de-servico/
https://www.portaldeangola.com/pr-realca-crescimento-das-tics/
https://www.portaldeangola.com/china-ja-reagiu-a-decisao-de-uniao-europeia-sobre-tarifas-nos-carros-eletricos/
https://www.portaldeangola.com/africa-do-sul-pros-e-contras-de-governo-de-unidade-nacional/
https://www.portaldeangola.com/jerry-west-o-logotipo-da-nba-morre-aos-86-anos/
https://www.portaldeangola.com/morreu-antigo-primeiro-ministro-franca-van-dunem/
https://www.portaldeangola.com/o-puzzle-dos-altos-cargos-da-ue-esta-quase-resolvido-e-antonio-costa-e-o-favorito-para-presidente-do-conselho-europeu/
https://www.portaldeangola.com/os-mercados-financeiros-aguardam-ansiosamente-a-decisao-do-fed-sobre-as-taxas-de-juro-esta-quarta-feira/
https://www.portaldeangola.com/italia-prepara-plano-do-g-7-para-seguranca-alimentar-e-energetica-em-africa/
https://www.portaldeangola.com/lider-da-extrema-direita-britanica-e-atingido-por-objetos-durante-ato-de-campanha/
https://www.portaldeangola.com/hunter-biden-filho-do-presidente-dos-eua-e-condenado-por-mentir-sobre-uso-de-drogas-para-comprar-arma/
https://www.portaldeangola.com/singapore-airlines-oferece-indemnizacao-aos-passageiros-de-voo-que-sofreu-turbulencia/
https://www.portaldeangola.com/base-militar-dos-eua-custaria-a-subserviencia-de-luanda/
https://www.portaldeangola.com/sme-repatria-133-cidadaos-da-rdc-por-irregularidades-migratorias/
https://www.portaldeangola.com/fed-mantera-suas-taxas-de-olho-na-inflacao/
https://www.portaldeangola.com/em-telefonema-com-putin-lula-reafirma-defesa-de-negociacoes-de-paz-que-envolvam-russia-e-ucrania/
https://www.portaldeangola.com/guine-bissau-jovens-dos-partidos-prometem-combater-regime/
https://www.portaldeangola.com/desaparece-aviao-com-vice-presidente-do-malawi-e-mais-nove-pessoas-a-bordo/
https://www.portaldeangola.com/bilhetes-para-o-angola-camaroes-variam-entre-1000-e-18-mil-kwanzas/
https://www.portaldeangola.com/mais-de-20-paises-assinam-na-costa-rica-declaracao-de-paz-ao-oceano/
https://www.portaldeangola.com/eleicoes-europeias-europa-escolhe-novo-parlamento/
https://www.portaldeangola.com/por-que-ha-excesso-de-oferta-de-coca-na-america-latina-e-qual-o-impacto-no-mercado-de-cocaina/
https://www.portaldeangola.com/angola-partilha-experiencia-sobre-economia-azul/
https://www.portaldeangola.com/dubai-podera-estar-a-proteger-isabel-dos-santos/
https://www.portaldeangola.com/israel-resgata-quatro-refens-em-gaza-e-palestinos-dizem-que-93-foram-mortos-em-ataque-israelita/
https://www.portaldeangola.com/primeira-ministra-da-dinamarca-atacada-em-copenhaga/
https://www.portaldeangola.com/proteger-os-oceanos-e-imperativo-alerta-forum-na-costa-rica/
https://www.portaldeangola.com/putin-diz-que-russia-nao-precisa-usar-armas-nucleares-para-vencer-na-ucrania/
https://www.portaldeangola.com/lula-milei-e-papa-francisco-participarao-de-cimeira-do-g7-na-italia/
https://www.portaldeangola.com/rdc-comecou-julgamento-de-50-pessoas-acusadas-de-tentativa-de-golpe/
https://www.portaldeangola.com/rebeldes-houthi-detemrebeldes-houthi-detem-pelo-menos-9-membros-da-onu-dizem-as-autoridades-pelo-menos-9-membros-da-onu-dizem-as-autoridades/
https://www.portaldeangola.com/fmi-tem-ajudado-angola-a-enfrentar-desequilibrios-economicos-diz-patricio-neto/
https://www.portaldeangola.com/angola-eleita-vice-presidente-da-agnu79/
https://www.portaldeangola.com/angola-e-eua-assinam-acordo-de-cooperacao-militar/
https://www.portaldeangola.com/angola-e-eua-lancam-programa-de-fortalecimento-dos-partidos-politicos/
https://www.portaldeangola.com/ucraniano-pro-russo-detido-em-hospital-frances-por-suspeita-de-planear-um-atentado/
https://www.portaldeangola.com/julgamento-do-filho-de-biden-continua-nos-eua-com-depoimento-da-ex-esposa/
https://www.portaldeangola.com/mundo-entra-em-sequencia-de-temperaturas-recordes-e-onu-alerta-para-inferno-climatico/
https://www.portaldeangola.com/combate-a-corrupcao-em-angola-a-nova-estrategia-chega/
https://www.portaldeangola.com/angola-lng-atinge-pico-de-producao-em-2025/
https://www.portaldeangola.com/minerais-de-terra-rara-abundam-em-angola/
https://www.portaldeangola.com/o-plano-ambicioso-do-quenia-para-se-tornar-um-centro-de-tecnologia-limpa-em-africa/
https://www.portaldeangola.com/greve-na-nigeria-fecha-rede-eletrica-e-perturba-companhias-aereas/
https://www.portaldeangola.com/o-fmi-deve-atender-as-necessidades-dos-seus-membros-globais-e-adaptar-se-aos-desafios-emergentes-afirma-o-presidente-do-quenia/
https://www.portaldeangola.com/o-bce-prepara-se-para-baixar-as-taxas-de-juro-na-zona-euro-esta-semana-num-contexto-de-muita-incerteza-economica/
https://www.portaldeangola.com/as-quotas-de-producao-de-petroleo-voltam-a-ameacar-a-coesao-da-opep-apos-a-saida-de-angola-no-final-de-2023/
https://www.portaldeangola.com/o-que-esta-por-tras-da-onda-de-sequestros-na-nigeria/
https://www.portaldeangola.com/israel-continua-bombardeando-gaza-apos-novo-pedido-de-cessar-fogo/
https://www.portaldeangola.com/trump-adere-ao-tiktok-rede-que-queria-banir-quando-estava-no-cargo/
https://www.portaldeangola.com/quarenta-e-oito-paises-africanos-vao-participar-na-cimeira-coreia-do-sul-africa/
https://www.portaldeangola.com/angola-conquista-mais-de-100-medalhas/
https://www.portaldeangola.com/sonda-chinesa-chega-a-face-oculta-da-lua-para-recolher-amostras/
https://www.portaldeangola.com/anc-perde-sua-maioria-historica-no-parlamento-sul-africano-e-busca-coligacoes/
https://www.portaldeangola.com/liga-dos-campeoes-real-madrid-conquista-la-15a/
https://www.portaldeangola.com/hamas-considera-positiva-nova-proposta-israelita-para-tregua-em-gaza/
https://www.portaldeangola.com/biden-tem-2-pontos-de-vantagem-sobre-trump-apos-condenacao-de-republicano-aponta-pesquisa-reuters-ipsos/
https://www.portaldeangola.com/estado-da-uniao-os-desafios-para-a-europa-da-nova-geopolitica/
https://www.portaldeangola.com/pgr-angolana-continua-empenhada-a-recuperar-ativos/
https://www.portaldeangola.com/angola-concorda-com-visto-comum-para-turismo-em-paises-da-africa-austral/
https://www.portaldeangola.com/israel-intensifica-ofensiva-em-rafah-apos-tomar-corredor-entre-gaza-e-egito/
https://www.portaldeangola.com/joe-biden-vai-autorizar-ucrania-a-utilizar-armamento-norte-americano-contra-alvos-em-solo-russo/
https://www.portaldeangola.com/angola-e-os-estados-unidos-aprofundam-cooperacao-militar/
https://www.portaldeangola.com/o-anc-esta-em-terreno-desconhecido-para-governar-a-africa-do-sul-indicam-os-primeiros-resultados-eleitorais/
https://www.portaldeangola.com/donald-trump-e-considerado-culpado-de-todas-as-acusacoes-no-caso-hush-money-em-nova-york/
https://www.portaldeangola.com/azerbaijao-anfitriao-da-cop29-trabalha-em-proposta-para-impor-um-imposto-global-sobre-os-combustiveis-fosseis/
https://www.portaldeangola.com/a-voz-da-africa-precisa-de-ser-ouvida-afirmou-o-presidente-do-banco-africano-de-desenvolvimento/
https://www.portaldeangola.com/empresas-francesas-americanas-russas-e-chinesas-competem-para-construir-a-primeira-central-nuclear-do-gana/
https://www.portaldeangola.com/fmi-eleva-previsao-de-crescimento-da-china-para-5-citando-rapido-no-inicio-de-2024/
https://www.portaldeangola.com/a-industria-petrolifera-do-canada-esta-em-expansao-mas-as-empresas-lutam-para-contratar-e-reter-talentos-qualificados/
https://www.portaldeangola.com/a-opacidade-da-estrategia-da-opep-de-reducao-da-producao-de-petroleo-esta-a-minar-a-credibilidade-do-cartel/
https://www.portaldeangola.com/policia-faz-novas-buscas-no-caso-de-influencia-russa-no-parlamento-europeu/
https://www.portaldeangola.com/comite-conjunto-de-defesa-estados-unidos-angola-reune-se-na-proxima-semana/
https://www.portaldeangola.com/ue-e-australia-assinam-pacto-de-minerais-criticos-para-diversificar-cadeias-de-abastecimento/
https://www.portaldeangola.com/investimentos-em-petroleo-e-gas-na-noruega-atingirao-recorde-em-2024-apesar-de-ser-um-pais-lider-na-transicao-energetica/
https://www.portaldeangola.com/a-china-esta-de-volta-a-africa-desta-vez-com-mais-investimentos-e-menos-emprestimos/
https://www.portaldeangola.com/angola-indicios-de-escandalo-financeiro-abalam-administracao-geral-tributaria/
https://www.portaldeangola.com/quem-compete-com-o-brasil-pela-lideranca-do-sul-global/
https://www.portaldeangola.com/sanchez-sobre-reconhecimento-da-palestina-nao-e-uma-decisao-que-adotamos-contra-alguem/
https://www.portaldeangola.com/ativistas-em-bissau-nao-cometemos-nenhum-crime/
https://www.portaldeangola.com/palestinianos-acusam-israel-de-massacre-em-ataques-a-deslocados-em-rafah/
https://www.portaldeangola.com/27-de-maio-orfaos-denunciam-erros-na-investigacao/
https://www.portaldeangola.com/stand-do-bci-recebe-centenas-de-visitas-na-13-a-edicao-da-fib/
https://www.portaldeangola.com/emirados-arabes-unidos-atingirao-a-capacidade-petrolifera-de-5-milhoes-de-barris-por-dia-mais-cedo-do-que-o-esperado/
https://www.portaldeangola.com/a-cnooc-empresa-chinesa-de-energia-assina-acordo-petrolifero-com-mocambique/
https://www.portaldeangola.com/as-negociacoes-sobre-o-clima-estao-num-impasse-para-chegar-a-um-acordo-sobre-financiamento-para-as-nacoes-pobres/
https://www.portaldeangola.com/reuniao-do-g-7-critica-abertamente-as-praticas-comerciais-da-china-e-ameaca-tomar-medidas-coercivas/
https://www.portaldeangola.com/yellen-diz-que-os-estados-unidos-nao-estao-prontos-para-assinar-um-acordo-fiscal-global-liderado-pela-ocde/
https://www.portaldeangola.com/anora-de-sean-baker-vence-palma-de-ouro-em-cannes-miguel-gomes-recebe-melhor-realizacao-com-grand-tour/
https://www.portaldeangola.com/papa-francisco-abre-jornada-mundial-da-crianca-no-estadio-olimpico-de-roma/
https://www.portaldeangola.com/russia-continua-ataques-a-kharkiv-enquanto-tropas-ucranianas-recuperam-terreno/
https://www.portaldeangola.com/departamento-de-estado-eua-estao-profundamente-preocupados-com-exercicios-militares-da-china-no-estreito-de-taiwan/
https://www.portaldeangola.com/porto-do-namibe-aumenta-movimentacao-de-carga-para-275-mil-toneladas/
https://www.portaldeangola.com/como-e-que-italia-ve-a-abertura-de-ursula-von-der-leyen-para-cooperar-com-meloni/
https://www.portaldeangola.com/angola-tera-52-novos-postos-de-combustiveis-ate-2027/
https://www.portaldeangola.com/tribunal-internacional-da-justica-ordena-o-fim-da-ofensiva-de-israel-em-rafah/
https://www.portaldeangola.com/bissau-juiz-ordena-libertacao-de-ativistas/
https://www.portaldeangola.com/a-europa-consegue-assegurar-seus-proprios-minerais-criticos/
https://www.portaldeangola.com/proposta-da-unita-das-autarquias-aprovada-pelo-parlamento/
https://www.portaldeangola.com/advogados-do-congo-afirmam-ter-novas-evidencias-comprometedoras-sobre-a-cadeia-de-fornecimento-de-minerais-da-apple/
https://www.portaldeangola.com/secretario-de-estado-destaca-importancia-do-recenseamento-da-populacao/
https://www.portaldeangola.com/financiamento-aos-paises-em-desenvolvimento-para-a-acao-climatica-beneficia-paises-ricos-revela-um-relatorio-da-reuters/
https://www.portaldeangola.com/os-eua-e-o-quenia-lancam-a-visao-nairobi-washington-sobre-a-divida-e-o-investimento-sustentavel-nos-paises-em-desenvolvimento/
https://www.portaldeangola.com/angola-dois-anos-ao-servico-da-paz-em-africa/
https://www.portaldeangola.com/africa-do-sul-considera-apresentar-queixa-a-omc-contra-o-imposto-fronteirico-sobre-carbono-da-eu/
https://www.portaldeangola.com/eua-deve-designar-o-quenia-como-parceiro-estrategico-fora-da-otan-e-quer-aumentar-a-cooperacao-tecnologica-entre-os-dois-paises/
https://www.portaldeangola.com/espanha-e-irlanda-tentam-que-ue-se-incline-para-o-reconhecimento-da-palestina/
https://www.portaldeangola.com/joao-lourenco-declina-convite-para-paricipar-em-cimeira-pela-paz-na-ucrania/
https://www.portaldeangola.com/aumentam-denuncias-de-violencia-contra-as-mulheres-angolanas/
https://www.portaldeangola.com/fib-2024-arranca-com-aumento-do-numero-de-expositores/
https://www.portaldeangola.com/a-economia-angolana-continua-presa-ao-estado-omnipresente-segundo-o-economista-angolano-yuri-quixina/
https://www.portaldeangola.com/haddad-diz-temer-que-tragedia-no-rs-sirva-de-argumento-para-politica-monetaria-restritiva/
https://www.portaldeangola.com/primeiro-ministro-britanico-convoca-eleicoes-antecipadas-para-4-de-julho-enquanto-o-seu-partido-perde-nas-sondagens/
https://www.portaldeangola.com/a-china-esta-a-vencer-a-corrida-pelos-minerais-essenciais-para-a-transicao-energetica/
https://www.portaldeangola.com/espanha-e-irlanda-reconhecem-hoje-o-estado-palestino/
https://www.portaldeangola.com/a-costa-do-marfim-tornou-se-o-pais-com-a-melhor-classificacao-da-divida-publica-na-africa-subsaariana/
https://www.portaldeangola.com/preco-do-petroleo-continua-a-oscilar-numa-faixa-estreita-nao-dando-indicacoes-claras-sobre-o-sentimento-do-mercado/
https://www.portaldeangola.com/presidente-da-republica-recebe-pca-da-totalenergies-enquanto-producao-de-petroleo-em-angola-cai-para-1083-milhoes-bd/
https://www.portaldeangola.com/china-ameaca-retaliar-contra-a-ue-num-agravamento-do-conflito-comercial-entre-os-dois-blocos/
https://www.portaldeangola.com/os-eua-pretendem-remodelar-as-cadeias-de-abastecimento-globais-na-asia-e-a-china-contorna-isso-com-investimentos-em-paises-asiaticos/
https://www.portaldeangola.com/a-mega-refinaria-dangote-da-nigeria-pretende-importar-milhoes-de-barris-de-petroleo-dos-eua/
https://www.portaldeangola.com/nas-vesperas-das-eleicoes-o-anc-na-africa-do-sul-caminha-na-corda-bamba-politica-sobre-o-encerramento-de-centrais-a-carvao/
https://www.portaldeangola.com/banco-central-da-nigeria-nao-consegue-conter-a-queda-do-naira/
https://www.portaldeangola.com/a-europa-conseguiu-navegar-com-sucesso-atraves-de-um-periodo-tumultuoso-diz-o-fmi/
https://www.portaldeangola.com/ia-generativa-ameaca-economia-dos-meios-de-comunicacao/
https://www.portaldeangola.com/tse-suspende-julgamento-de-acoes-que-pedem-cassacao-de-moro-por-atos-na-pre-campanha-em-2022-caso-sera-retomado-na-3a/
https://www.portaldeangola.com/espanha-recusou-autorizacao-para-escala-a-navio-que-transportava-armas-para-israel/
https://www.portaldeangola.com/15-paises-europeus-querem-novas-solucoes-para-transferir-migrantes-fora-da-ue/
https://www.portaldeangola.com/angolanos-contestam-novos-precos-dos-transportes-coletivos/
https://www.portaldeangola.com/estadista-angolano-recebe-principe-herdeiro-do-sultanato-de-oma/
https://www.portaldeangola.com/pr-trabalha-no-namibe/
https://www.portaldeangola.com/angola-e-china-avaliam-cooperacao-bilateral/
https://www.portaldeangola.com/presidente-da-republica-recomenda-aumento-da-producao-de-petroleo-e-gas/
https://www.portaldeangola.com/excesso-de-capacidade-na-industria-siderurgica-da-china-se-espalha-para-os-mercados-de-exportacao/
https://www.portaldeangola.com/o-petroleo-oscila-a-medida-que-o-clima-de-risco-e-compensado-pela-previsao-de-demanda-mais-fraca-da-aie/
https://www.portaldeangola.com/a-inflacao-nos-eua-cai-pela-primeira-vez-em-seis-meses-abrindo-caminho-para-que-o-fed-comece-a-reduzir-as-taxas-de-juros/
https://www.portaldeangola.com/cacau-cai-19-enquanto-previsoes-de-chuva-provocam-volatilidade-no-mercado/
https://www.portaldeangola.com/microsoft-impoe-requisitos-climaticos-aos-fornecedores-num-esforco-para-reduzir-as-suas-emissoes-de-carbono/
https://www.portaldeangola.com/primeiro-ministro-da-eslovaquia-em-risco-de-vida-depois-de-ter-sido-baleado-no-estomago/
https://www.portaldeangola.com/partidos-de-direita-chegam-a-acordo-sobre-nova-coligacao-nos-paises-baixos/
https://www.portaldeangola.com/cimeira-sobre-tecnologias-e-combustiveis-limpos-para-cozinhar-em-africa-mobiliza-22-mil-milhoes-de-dolares/
https://www.portaldeangola.com/presidente-da-republica-reconduz-conselho-de-administracao-da-sonangol/
https://www.portaldeangola.com/afastamento-de-embaixador-revela-dupla-face-dos-eua/
https://www.portaldeangola.com/taag-retoma-voos-na-rota-luanda-lisboa/
https://www.portaldeangola.com/em-kiev-blinken-promete-apoio-inabalavel-dos-eua-a-ucrania-enquanto-russia-intensifica-ataques/
https://www.portaldeangola.com/a-poesia-habita-me-ela-mora-dentro-de-mim/
https://www.portaldeangola.com/portela-vai-ser-alargada-alcochete-e-a-escolha-final-para-o-novo-aeroporto/
https://www.portaldeangola.com/comissao-economica-analisa-programacao-financeira/
https://www.portaldeangola.com/comandante-geral-da-policia-admite-envolvimento-de-agentes-em-raptos-e-assaltos/
https://www.portaldeangola.com/eni-pretende-desmembrar-projetos-de-petroleo-e-gas-para-se-adaptar-as-exigencias-do-mercado-energetico-em-mudanca/
https://www.portaldeangola.com/grupo-bhp-aumenta-pressao-para-adquirir-a-anglo-american-numa-estrategia-para-controlar-a-producao-de-cobre/
https://www.portaldeangola.com/pgr-de-angola-em-genebra-em-esforco-para-recuperar-ativos-do-estado-desviados-por-corrupcao/
https://www.portaldeangola.com/angola-e-zimbabwe-discutem-reforco-da-cooperacao/
https://www.portaldeangola.com/estudos-sobre-angola-devem-focar-se-na-multiculturalidade/
https://www.portaldeangola.com/a-batalha-global-de-chips-entre-os-eua-ue-e-a-china-intensifica-se-com-o-aumento-dos-subsidios-e-restricoes-comerciais/
https://www.portaldeangola.com/eua-e-china-procuram-colaboracao-em-materia-de-clima-apesar-das-tensoes-politicas-e-economicas/
https://www.portaldeangola.com/aie-organiza-cimeira-sobre-tecnologias-e-combustiveis-limpos-para-cozinhar-em-africa-no-dia-14-de-maio/
https://www.portaldeangola.com/fundo-da-arabia-saudita-para-tecnologia-de-chips-e-ia-pronto-para-abandonar-parceria-com-a-china-se-os-eua-pedirem/
https://www.portaldeangola.com/fontes-renovaveis-forneceram-um-recorde-de-30-da-eletricidade-no-ano-passado/
https://www.portaldeangola.com/suica-vence-festival-de-musica-eurovision/
https://www.portaldeangola.com/ativistas-climaticos-pressionam-biden-para-interromper-as-exportacoes-de-petroleo-do-novo-terminal-petrolifero/
https://www.portaldeangola.com/rui-falcao-defende-a-presenca-dos-melhores-no-afrobasket2025/
https://www.portaldeangola.com/novo-presidente-do-senegal-anuncia-auditoria-aos-acordos-de-pesca-com-a-uniao-europeia/
https://www.portaldeangola.com/fmi-e-rd-congo-chegam-a-acordo-sobre-revisao-final-do-programa-de-emprestimo/
https://www.portaldeangola.com/africa-do-sul-pode-restringir-a-exploracao-de-petroleo-da-shell-se-a-empresa-abandonar-as-operacoes-downstream/
https://www.portaldeangola.com/fmi-elogia-as-reformas-economicas-na-nigeria/
https://www.portaldeangola.com/a-reabilitacao-de-david-cameron-como-ministro-das-relacoes-exteriores-apos-seu-fracasso-no-brexit/
https://www.portaldeangola.com/easyjet-anuncia-voos-low-cost-de-portugal-para-cabo-verde/
https://www.portaldeangola.com/guine-bissau-e-parceiro-firme-da-russia-diz-sissoco-embalo-a-vladimir-putin/
https://www.portaldeangola.com/cantora-israelense-se-classifica-para-final-do-eurovision-apos-criticas-em-ato-pro-palestinos/
https://www.portaldeangola.com/ramon-fonseca-um-dos-chefes-do-escritorio-de-advocacia-dos-panama-papers-morre-aos-71-anos/
https://www.portaldeangola.com/parlamentares-aprovam-pena-maxima-de-oito-anos-para-crimes-de-violacao-a-menor/
https://www.portaldeangola.com/governo-sao-tomense-defende-acordo-militar-com-a-russia/
https://www.portaldeangola.com/rdc-ruanda-por-detras-dos-ataques-aos-deslocados-internos/
https://www.portaldeangola.com/sem-fundos-para-eleicoes-e-necessario-tomar-diligencias/
https://www.portaldeangola.com/angola-obtem-usd-1-3-mil-milhoes-de-instituicoes-americanas/
https://www.portaldeangola.com/biden-lanca-vasto-projeto-da-microsoft-no-mesmo-local-de-promessa-nao-cumprida-por-trump/
https://www.portaldeangola.com/emprego-em-maximos-historicos-portugal-tem-mais-de-5-milhoes-de-trabalhadores/
https://www.portaldeangola.com/acordo-com-a-china-da-a-angola-mais-de-150-milhoes-de-dolares-mensais-sem-restruturacao-da-divida-disse-vera-daves/
https://www.portaldeangola.com/ue-vai-usar-3-mil-milhoes-de-euros-de-lucros-de-ativos-russos-para-ajudar-ucrania/
https://www.portaldeangola.com/bancos-comerciais-adquirem-usd-200-milhoes-disponibilizados-pelo-bna/
https://www.portaldeangola.com/ex-colonias-portuguesas-sao-o-proximo-alvo-da-russia-sao-tome-assina-acordo-de-cooperacao-militar-com-moscovo-que-pode-nao-ficar-por-aqui/
https://www.portaldeangola.com/acordo-com-eximbank-reforca-capacidade-energetica-do-pais/
https://www.portaldeangola.com/joao-lourenco-termina-participacao-na-cimeira-de-dallas/
https://www.portaldeangola.com/banco-mundial-aprova-emprestimo-de-1385-milhoes-de-dolares-a-namibia-para-a-transicao-energetica/
https://www.portaldeangola.com/amazon-lanca-servico-de-compras-online-na-africa-do-sul/
https://www.portaldeangola.com/aramco-paga-dividendos-de-us-31-mil-milhoes-para-ajudar-a-financiar-o-deficit-orcamentario-da-arabia-saudita/
https://www.portaldeangola.com/precos-da-energia-e-do-gas-natural-nos-eua-caem-abaixo-de-zero-enquanto-as-atencoes-agora-se-voltam-para-a-opep/
https://www.portaldeangola.com/preco-do-petroleo-baixa-a-medida-que-as-tensoes-na-oferta-diminuem/
https://www.portaldeangola.com/chega-avanca-com-proposta-para-criminalizar-marcelo-por-traicao-a-patria/
https://www.portaldeangola.com/joao-lourenco-solicita-maior-equilibrio-da-divida-publica-dos-paises-africanos/
https://www.portaldeangola.com/pr-discute-parcerias-com-multinacionais-americanas/
https://www.portaldeangola.com/a-exploracao-de-petroleo-em-aguas-profundas-esta-a-ganhar-novo-impulso/
https://www.portaldeangola.com/a-corrida-pelo-dominio-do-hidrogenio-verde-esta-a-acelerar/
https://www.portaldeangola.com/xi-diz-que-a-china-quer-evitar-uma-nova-guerra-fria-e-a-ue-diz-estar-pronta-para-se-defender-comercialmente-contra-a-china/
https://www.portaldeangola.com/boeing-estuda-parceria-estrategica-com-angola/
https://www.portaldeangola.com/presidente-frances-apela-ao-restabelecimento-dos-lacos-economicos-com-a-china/
https://www.portaldeangola.com/preco-do-cafe-robusta-atinge-maximo-desde-1970-disse-a-oic/
https://www.portaldeangola.com/sera-o-estado-angolano-agora-o-principal-adversario-da-economia/
https://www.portaldeangola.com/mais-de-16-milhoes-de-pessoas-assistiram-ao-concerto-de-madonna-no-rio-de-janeiro/
https://www.portaldeangola.com/daniel-chapo-e-o-candidato-da-frelimo-as-presidenciais/
https://www.portaldeangola.com/futebol-sporting-cp-sagrou-se-campeao-de-portugal/
https://www.portaldeangola.com/africano-de-natacao-domina-semana-desportiva/
https://www.portaldeangola.com/mpla-e-swapo-reforcam-relacoes-bilaterais/
https://www.portaldeangola.com/presidente-joe-biden-propoe-nova-embaixadora-para-angola/
https://www.portaldeangola.com/girabola2023-24-kabuscorp-derrota-sao-salvador-nos-coqueiros/
https://www.portaldeangola.com/jovens-tentam-legalizar-novo-partido-em-angola/
https://www.portaldeangola.com/estados-unidos-e-a-arabia-saudita-estao-proximos-de-um-acordo-que-visa-remodelar-a-geopolitica-do-medio-oriente/
https://www.portaldeangola.com/porto-de-antuerpia-na-belgica-planeia-porto-de-transporte-de-hidrogenio-na-namibia-de-e-250-milhoes/
https://www.portaldeangola.com/exxonmobil-avanca-com-projecto-de-gnl-de-mocambique-diz-um-responsavel/
https://www.portaldeangola.com/em-vesperas-de-eleicoes-governo-sul-africano-gasta-milhares-de-milhoes-de-rands-para-manter-a-electricidade-a-funcionar/
https://www.portaldeangola.com/costa-identifica-problemas-de-ponderacao-em-marcelo-e-prefere-ter-explicacoes-da-pgr-em-tribunal-em-vez-de-no-parlamento/
https://www.portaldeangola.com/orangotango-selvagem-curou-ferida-com-unguento-que-ele-preparou-dizem-cientistas/
https://www.portaldeangola.com/sao-tome-quer-reparacoes-de-portugal-por-colonizacao/
https://www.portaldeangola.com/ministro-quer-medidas-mais-adequadas-contra-o-vandalismo-de-bens-publicos/
https://www.portaldeangola.com/pgr-destaca-rapida-adaptacao-dos-juizes-de-garantias/
https://www.portaldeangola.com/administracoes-assumem-gestao-dos-espacos-infra-estruturados-das-centralidades-de-benguela/
https://www.portaldeangola.com/tarrafal-e-a-memoria/
https://www.portaldeangola.com/estados-unidos-fed-afirma-que-o-progresso-na-luta-contra-a-inflacao-estagnou-e-mantem-as-taxas-de-juro-elevadas/
https://www.portaldeangola.com/chuvas-afetam-fase-final-da-safra-de-soja-e-milho-do-rio-grande-do-sul/
https://www.portaldeangola.com/perspetivas-economicas-da-ocde-crescimento-global-estavel-esperado-para-2024-e-2025/
https://www.portaldeangola.com/para-a-historia-o-ceticismo-de-fidel-castro-e-nikita-krushchev-sobre-a-revolucao-em-africa/
https://www.portaldeangola.com/juizes-de-garantia-avaliam-cerca-de-vinte-mil-processos-em-um-ano/
https://www.portaldeangola.com/moodys-eleva-perspetiva-de-credito-do-brasil-para-positiva-com-base-no-progresso-das-reformas-economicas/
https://www.portaldeangola.com/a-situacao-economica-da-nigeria-piora-a-medida-que-os-precos-da-gasolina-disparam-e-a-inflacao-aumenta/
https://www.portaldeangola.com/portugal-reparacao-as-ex-colonias-esta-a-ser-feita/
https://www.portaldeangola.com/embaixador-realca-importancia-do-terminal-de-aguas-profundas/
https://www.portaldeangola.com/festas-da-cidade-de-benguela-de-regresso-com-varios-atractivos-culturais/
https://www.portaldeangola.com/presidente-do-banco-mundial-espera-que-nacoes-ricas-atendam-aos-pedidos-dos-lideres-africanos/
https://www.portaldeangola.com/galp-vai-precisar-de-parceiro-para-ajudar-a-desenvolver-bloco-petrolifero-da-namibia-diz-ceo/
https://www.portaldeangola.com/lucro-da-huawei-aumenta-564-ao-eclipsar-a-apple-na-china/
https://www.portaldeangola.com/producao-de-petroleo-da-opep-cai-em-abril-liderada-pelo-irao-iraque-e-nigeria-revela-a-reuters/
https://www.portaldeangola.com/podera-xi-jinping-convencer-a-europa-a-desempenhar-o-papel-de-fiel-da-balanca-entre-a-china-e-os-eua/
https://www.portaldeangola.com/mesmo-com-tregua-em-gaza-israel-nao-descarta-invadir-rafah-diz-netanyahu/
https://www.portaldeangola.com/cabo-verde-pr-pede-debate-sereno-por-reparacoes-coloniais/
https://www.portaldeangola.com/greve-na-administracao-publica-com-impactos-na-economia-e-na-politica/
https://www.portaldeangola.com/apostar-no-desporto-sera-sempre-um-investimento-rui-falcao/
https://www.portaldeangola.com/comunicacao-social-considerada-fundamental-para-credibilidade-do-censo-2024/
https://www.portaldeangola.com/o-regulamento-sobre-desflorestacao-da-ue-podera-afectar-milhares-de-agricultores-nos-paises-em-desenvolvimento/
https://www.portaldeangola.com/macron-diz-que-a-europa-ja-nao-pode-confiar-nos-eua-para-a-sua-seguranca-e-apela-a-uma-defesa-europeia-credivel/
https://www.portaldeangola.com/lideres-africanos-procuram-financiamento-recorde-do-banco-mundial-para-combater-as-alteracoes-climaticas/
https://www.portaldeangola.com/a-rd-congo-questiona-a-apple-sobre-a-utilizacao-de-minerais-de-conflito-na-sua-cadeia-de-abastecimento/
https://www.portaldeangola.com/ue-lanca-reflexao-para-rivalizar-com-o-vasto-plano-de-investimento-global-da-china-especialmente-em-africa/
https://www.portaldeangola.com/bna-aprova-visao-do-sistema-de-pagamento-em-novembro/
https://www.portaldeangola.com/aquisicao-de-combustivel-reduz-cerca-de-21-no-1o-trimestre/
https://www.portaldeangola.com/angola-pede-instalacao-de-fabricas-sul-coreanas/
https://www.portaldeangola.com/contagem-regressiva-para-a-cimeira-do-clima-cop29-no-azerbaijao-expoe-as-tensoes-sobre-o-financiamento/
https://www.portaldeangola.com/o-presidente-do-azerbaijao-anfitriao-da-cop29-afirma-que-o-seu-petroleo-e-um-presente-de-deus/
https://www.portaldeangola.com/o-cobre-sera-fundamental-para-a-transicao-energetica-a-medida-que-o-mundo-se-eletrifica/
https://www.portaldeangola.com/ceo-da-total-diz-que-o-mundo-deve-se-adaptar-ao-aquecimento-pois-a-sede-por-petroleo-persiste/
https://www.portaldeangola.com/ate-2050-a-populacao-em-idade-ativa-continuara-a-crescer-na-africa-subsaariana-mas-diminuira-no-resto-do-mundo-o-que-isso-significa/
https://www.portaldeangola.com/villas-boas-fala-em-noite-historica-o-fc-porto-esta-livre-de-novo/
https://www.portaldeangola.com/haddad-diz-que-e-extremamente-complexo-conviver-com-presidente-do-bc-que-voce-nao-escolheu/
https://www.portaldeangola.com/julgamento-de-trump-testa-estrategia-de-campanha-de-aproveitar-publicidade-ruim/
https://www.portaldeangola.com/presidente-de-portugal-sugere-cancelamento-de-divida-para-reparar-legado-colonial/
https://www.portaldeangola.com/brasil-nao-pode-entrar-apenas-como-vitima-em-debate-sobre-reparacao-de-portugal-pela-escravidao-diz-luiz-felipe-de-alencastro/
https://www.portaldeangola.com/hamas-promete-responder-a-proposta-de-israel-para-um-novo-acordo/
https://www.portaldeangola.com/o-mal-estar-dos-estudantes-judeus-com-os-protestos-nas-universidades-americanas/
https://www.portaldeangola.com/mumias-espontaneas-intrigam-cidade-colombiana/
https://www.portaldeangola.com/incendio-em-abrigo-deixa-10-mortos-em-porto-alegre/
https://www.portaldeangola.com/com-gripe-aviaria-se-espalhando-testes-nos-eua-mostram-que-leite-pasteurizado-e-seguro/
https://www.portaldeangola.com/alegada-detencao-de-procurador-guineense-apanhado-com-droga-em-lisboa/
https://www.portaldeangola.com/esquerda-segue-aguiar-branco-e-quer-lucilia-gago-no-parlamento-chega-esta-contra/
https://www.portaldeangola.com/casos-judiciais-podem-arrefecer-relacoes-historicas-entre-mocambique-e-africa-do-sul/
https://www.portaldeangola.com/antigo-primeiro-ministro-portugues-agradece-apoio-de-angola/
https://www.portaldeangola.com/juizes-da-suprema-corte-dos-eua-se-inclinam-para-algum-nivel-de-imunidade-ao-analisar-pedido-de-trump/
https://www.portaldeangola.com/portugal-celebra-50-anos-do-25-de-abril/
https://www.portaldeangola.com/governo-angolano-projecta-ligacao-dos-tres-corredores-ferroviarios-do-pais/
https://www.portaldeangola.com/mais-de-cem-mil-jovens-ingressam-no-mercado-de-trabalho/
https://www.portaldeangola.com/portugal-deve-pagar-custos-da-escravatura-e-dos-crimes-coloniais-diz-o-presidente-da-republica/
https://www.portaldeangola.com/brasil-adota-cautela-mas-recebe-recado-dos-eua-de-que-relacoes-serao-normais-mesmo-se-trump-ganhar/
https://www.portaldeangola.com/marcelo-diz-a-jornalistas-estrangeiros-que-montenegro-e-rural-e-costa-oriental/
https://www.portaldeangola.com/a-divida-de-africa-e-os-emprestimos-opacos-apoiados-por-recursos-prejudicam-o-seu-potencial-alerta-novamente-o-presidente-do-bad/
https://www.portaldeangola.com/casa-dos-estudantes-do-imperio-berco-de-lideres-africanos/
https://www.portaldeangola.com/nigeria-planeia-comercializar-petroleo-bruto-e-gas-na-bolsa-de-mercadorias-e-futuros-de-lagos/
https://www.portaldeangola.com/angola-modernizacao-do-porto-de-luanda-com-financiamento-dos-emirados-arabes-unidos/
https://www.portaldeangola.com/a-dependencia-da-china-em-relacao-ao-carvao-persistira-apesar-das-metas-climaticas-globais/
https://www.portaldeangola.com/o-ministro-das-financas-da-zambia-afirma-que-a-era-da-divida-excessiva-com-a-china-acabou/
https://www.portaldeangola.com/aumento-dos-protestos-pro-palestinianos-nas-universidades-dos-eua/
https://www.portaldeangola.com/ministro-ve-correcao-de-rumo-na-petrobras-ceo-destaca-resultados/
https://www.portaldeangola.com/greve-geral-em-angola-sindicatos-denunciam-intimidacoes/
https://www.portaldeangola.com/fraude-eleitoral-e-influenciar-eleicao-trump-na-hora-da-verdade/
https://www.portaldeangola.com/policia-continua-a-ser-acusada-de-violacoes-contra-vendedeiras-de-rua/
https://www.portaldeangola.com/eua-anuncia-medida-para-proteger-informacoes-medicas-sobre-abortos/
https://www.portaldeangola.com/angola-e-nigeria-analisam-cooperacao-no-dominio-da-defesa/
https://www.portaldeangola.com/ue-aprova-novas-sancoes-contra-o-irao-para-reduzir-a-producao-de-drones-e-misseis/
https://www.portaldeangola.com/despesas-militares-mundiais-atingem-novos-maximos-historicos/
https://www.portaldeangola.com/bolsonaro-exalta-musk-e-nega-tentativa-de-golpe-durante-manifestacao-em-copacabana/
https://www.portaldeangola.com/como-um-homem-enfureceu-o-seu-partido-e-arriscou-o-emprego-para-garantir-o-pacote-de-ajuda-dos-eua-a-ucrania/
https://www.portaldeangola.com/netanyahu-diz-que-lutara-contra-quaisquer-sancoes-impostas-ao-exercito-israelita/
https://www.portaldeangola.com/governante-convida-igrejas-a-manter-parceria-com-estado/
https://www.portaldeangola.com/can2024-angola-vice-campea-africana-de-futsal/
https://www.portaldeangola.com/ataque-aereo-causa-pelo-menos-nove-mortos-em-rafah/
https://www.portaldeangola.com/morre-homem-que-queimou-o-proprio-corpo-em-frente-ao-tribunal-onde-trump-e-julgado/
https://www.portaldeangola.com/apos-entusiasmo-inicial-jornalismo-busca-respostas-para-desafios-da-ia/
https://www.portaldeangola.com/oposicao-venezuelana-tramita-candidatura-unica-a-presidencia/
https://www.portaldeangola.com/bancos-multilaterais-de-desenvolvimento-prometem-ate-us-400-bilhoes-a-mais-em-emprestimos/
https://www.portaldeangola.com/camara-aprova-pacote-de-ajuda-de-95-bilioes-de-dolares-para-ucrania-israel-e-taiwan/
https://www.portaldeangola.com/governo-privatiza-tv-zimbo-e-grafica-damer/
https://www.portaldeangola.com/terminam-audiencias-de-julgamento-por-escandalo-panama-papers/
https://www.portaldeangola.com/boxe-kembo-nas-meias-finais-da-taca-nelson-mandela/
https://www.portaldeangola.com/polemica-na-argentina-por-aumento-de-salarios-de-senadores-em-plena-crise/
https://www.portaldeangola.com/musk-proprietario-do-x-se-opoe-a-proibicao-de-seu-competidor-tiktok-nos-eua/
https://www.portaldeangola.com/exportacoes-de-portugal-para-angola-chegam-aos-22-mil-milhoes-de-euros/
https://www.portaldeangola.com/angola-com-dificuldades-de-recuperar-ativos-de-sao-vicente/
https://www.portaldeangola.com/comandante-das-forcas-armadas-do-quenia-morre-em-acidente-de-helicoptero/
https://www.portaldeangola.com/o-que-se-sabe-ate-agora-sobre-ataque-israelense-ao-ira-na-madrugada/
https://www.portaldeangola.com/cimeira-ue-lideres-chegam-a-acordo-para-criar-novo-pacto-de-competitividade-para-reforcar-o-mercado-unico/
https://www.portaldeangola.com/fmi-altera-regras-para-acelerar-acordos-de-divida-com-paises-em-desenvolvimento-e-evitar-atrasos-causados-pela-china/
https://www.portaldeangola.com/ate-que-ponto-pode-a-politica-monetaria-do-bce-na-ue-divergir-da-politica-do-fed-nos-estados-unidos/
https://www.portaldeangola.com/o-futuro-do-tiktok-nos-estados-unidos-podera-ficar-decidido-esta-semana/
https://www.portaldeangola.com/ministro-realca-importancia-da-formacao-dos-investigadores-e-instrutores-processuais/
https://www.portaldeangola.com/angola-e-costa-do-marfim-defendem-cooperacao-ambiciosa-e-frutuosa/
https://www.portaldeangola.com/angola-pgr-conclui-o-processo-contra-isabel-dos-santos-e-faz-o-ponto-de-situacao-de-outros-processos-emblematicos/
https://www.portaldeangola.com/ucrania-lanca-ataque-com-misseis-norte-americanos-a-base-aerea-russa-na-crimeia/
https://www.portaldeangola.com/estados-unidos-podem-impor-sancoes-petroliferas-a-venezuela-na-quinta-feira/
https://www.portaldeangola.com/lideres-da-ue-vao-apelar-a-uma-mudanca-de-paradigma-para-inverter-o-declinio-europeu/
https://www.portaldeangola.com/sera-que-o-fed-conseguiu-domesticar-a-inflacao-nos-estados-unidos/
https://www.portaldeangola.com/biden-aumenta-tarifas-sobre-o-aco-chines-enquanto-promete-manter-a-siderurgia-dos-eua-propriedade-de-americanos/
https://www.portaldeangola.com/o-fmi-apela-a-consolidacao-fiscal-num-cenario-de-crescimento-moderado-e-divida-publica-crescente/
https://www.portaldeangola.com/relacao-diz-que-nao-ha-qualquer-indicio-de-que-antonio-costa-tenha-falado-com-lacerda-machado-sobre-sines/
https://www.portaldeangola.com/jornalista-do-novo-jornal-vence-segunda-edicao-do-premio-catoca/
https://www.portaldeangola.com/nigeria-aumenta-reservas-de-petroleo-em-1-bilhao-de-barris-consolidando-a-sua-posicao-de-lider-na-africa-subsaariana/
https://www.portaldeangola.com/fmi-alerta-os-estados-unidos-sobre-gastos-excessivos-e-aumento-da-divida/
https://www.portaldeangola.com/a-economia-global-permanece-resiliente-apesar-do-crescimento-desigual-e-dos-desafios-futuros-diz-fmi/
https://www.portaldeangola.com/depois-da-secretaria-do-tesouro-dos-eua-chanceler-alemao-chega-a-china-com-a-missao-de-reduzir-as-tensoes-economicas/
https://www.portaldeangola.com/gana-nao-chega-a-acordo-sobre-a-divida-com-detentores-privados-de-titulos-internacionais/
https://www.portaldeangola.com/america-latina-pretende-competir-com-o-sudeste-asiatico-na-producao-de-oleo-de-palma/
https://www.portaldeangola.com/a-europa-esta-atras-da-china-e-eua-apos-erros-energeticos-monumentais-diz-director-da-aie/
https://www.portaldeangola.com/opep-corteja-a-namibia-enquanto-o-pais-se-prepara-para-ser-o-quarto-maior-produtor-de-petroleo-de-africa/
https://www.portaldeangola.com/analistas-avaliam-preco-do-petroleo-apos-ataque-do-irao-a-israel/
https://www.portaldeangola.com/alerta-de-seguranca-iphones-de-92-paises-sob-ameaca-de-spyware/
https://www.portaldeangola.com/dois-ataques-e-uma-retaliacao-a-caminho-israel-vs-irao-e-uma-historia-sobre-a-legitima-defesa/
https://www.portaldeangola.com/piratas-que-desviaram-navio-proveniente-de-mocambique-foram-capturados/
https://www.portaldeangola.com/indice-de-precos-ao-consumidor-regista-ligeiro-abrandamento/
https://www.portaldeangola.com/haiti-ja-tem-conselho-presidencial-mas-ainda-nao-se-sabe-quem-vai-liderar-o-pais/
https://www.portaldeangola.com/comandante-geral-da-pn-anuncia-reforco-da-vigilancia-nos-postos-fronteiricos-do-pais/
https://www.portaldeangola.com/rui-falcao-quer-reflexao-sobre-contribuicao-dos-jovens/
https://www.portaldeangola.com/irao-lanca-ataque-com-mais-de-100-drones-contra-israel-em-retaliacao/
https://www.portaldeangola.com/navio-capturado-pelo-irao-tem-bandeira-portuguesa/
https://www.portaldeangola.com/ataque-a-facada-causa-pelo-menos-seis-mortos-em-centro-comercial-em-sydney/
https://www.portaldeangola.com/abel-chivukuvuku-continua-na-lideranca-do-pra-ja/
https://www.portaldeangola.com/os-custos-elevados-da-transicao-energetica-dificultam-a-implementacao-do-acordo-verde-da-uniao-europeia/
https://www.portaldeangola.com/onu-alerta-para-falta-de-investimento-para-atingir-os-objetivos-de-desenvolvimento-sustentavel-no-prazo-de-2030/
https://www.portaldeangola.com/al-hilal-oferece-mais-duas-epocas-de-contrato-para-jorge-jesus/
https://www.portaldeangola.com/cuando-cubango-ataque-a-caravana-da-unita-provoca-um-morto-e-quatro-feridos/
https://www.portaldeangola.com/camionistas-destacam-livre-circulacao-de-pessoas-e-bens-como-ganhos-da-paz/
https://www.portaldeangola.com/banco-central-europeu-mantem-taxas-de-juros-e-aponta-para-primeiro-corte-em-junho/
https://www.portaldeangola.com/tesouro-dos-eua-alerta-credores-oficiais-contra-o-desengajamento-na-ajuda-aos-paises-em-desenvolvimento/
https://www.portaldeangola.com/senadores-americanos-apresentam-projeto-de-lei-para-renovar-o-pacto-comercial-agoa-dos-eua-com-a-africa-ate-2041/
https://www.portaldeangola.com/a-cimeira-entre-os-eua-japao-e-filipinas-marca-um-ponto-de-viragem-critico-nas-relacoes-com-a-china-e-na-geopolitica-asiatica/
https://www.portaldeangola.com/presidentes-de-angola-e-de-cabo-verde-na-cimeira-empresarial-estados-unidos-africa/
https://www.portaldeangola.com/angola-governo-engajado-na-apresentacao-das-contas-publicas-a-tempo-diz-ministra-das-financas/
https://www.portaldeangola.com/angola-e-zambia-estarao-ligadas-por-oleoduto-diz-o-embaixador-da-zambia/
https://www.portaldeangola.com/shell-considera-deixar-a-bolsa-de-valores-de-londres/
https://www.portaldeangola.com/ue-quer-reforcar-a-sua-industria-para-atingir-as-metas-ambiciosas-do-acordo-verde/
https://www.portaldeangola.com/angola-academicos-analisam-politicas-sobre-fomento-do-crescimento-economico/
https://www.portaldeangola.com/os-altos-custos-de-energia-colocaram-a-industria-alema-em-desvantagem/
https://www.portaldeangola.com/o-setor-de-energia-supera-o-setor-de-tecnologia-no-mercado-de-acoes-dos-eua-gracas-ao-petroleo-e-ao-gas/
https://www.portaldeangola.com/presidente-da-assembleia-nacional-conversa-com-embaixadores-da-china-e-noruega/
https://www.portaldeangola.com/desportivo-despacha-kabuscorp-no-tundavala/
https://www.portaldeangola.com/inflacao-acima-do-esperado-nos-eua-reduz-perspectivas-de-cortes-nos-juros/
https://www.portaldeangola.com/fitch-corta-perspectiva-de-rating-da-china-devido-a-riscos-ao-crescimento/
https://www.portaldeangola.com/albanese-ue-deve-suspender-relacoes-com-israel-devido-ao-genocidio-em-gaza/
https://www.portaldeangola.com/agravamento-da-taxa-aduaneira-incentiva-a-producao-nacional/
https://www.portaldeangola.com/conflitos-podem-colocar-em-risco-projetos-petroliferos-na-africa-ocidental/
https://www.portaldeangola.com/o-ceo-do-jpmorgan-diz-que-pressionar-para-eliminar-todo-o-petroleo-e-gas-e-extremamente-ingenuo/
https://www.portaldeangola.com/visita-da-secretaria-do-tesouro-dos-eua-a-china-nao-resultou-em-acordos-concretos-para-reduzir-as-tensoes-bilaterais/
https://www.portaldeangola.com/africa-360o-3/
https://www.portaldeangola.com/as-economias-africanas-deverao-crescer-34-em-2024-diz-o-banco-mundial/
https://www.portaldeangola.com/openai-esgota-internet-para-explorar-superinteligencia-gpt-4/
https://www.portaldeangola.com/assembleia-nacional-acolhe-workshop-sobre-sistemas-de-financas-publicas/
https://www.portaldeangola.com/como-pode-a-india-tirar-a-coroa-do-crescimento-economico-a-china/
https://www.portaldeangola.com/tsmc-obtem-us-116-mil-milhoes-em-subsidios-e-emprestimos-dos-eua-para-fabricas-de-chips-made-in-america/
https://www.portaldeangola.com/para-presidente-do-jpmorgan-inflacao-continua-sendo-ameaca/
https://www.portaldeangola.com/mexico-eua-e-canada-engolidos-pela-escuridao-apos-eclipse-solar-total-veja-as-imagens/
https://www.portaldeangola.com/missao-da-uniao-europeia-ja-repeliu-11-ataques-dos-houthis-no-mar-vermelho/
https://www.portaldeangola.com/pr-do-ruanda-preocupado-com-posicao-dos-eua-sobre-genocidio/
https://www.portaldeangola.com/autoridades-procuram-20-desaparecidos-depois-de-naufragio-que-deixou-98-mortos/
https://www.portaldeangola.com/primeiro-ministro-cabo-verdiano-faz-forte-defesa-da-democracia-em-conferencia-internacional/
https://www.portaldeangola.com/divulgados-nomeados-da-10a-edicao-do-premios-sirius/
https://www.portaldeangola.com/a-probabilidade-do-petroleo-atingir-us-100-aumenta-a-medida-que-choques-de-oferta-convulsionam-o-mercado/
https://www.portaldeangola.com/africa-360o-2/
https://www.portaldeangola.com/estados-unidos-preparam-se-para-nova-luta-comercial-de-paineis-solares-importados-de-paises-do-sudeste-asiatico/
https://www.portaldeangola.com/a-franca-fornecera-subsidios-para-ajudar-os-fabricantes-de-paineis-solares-a-reduzir-o-dominio-da-china/
https://www.portaldeangola.com/genocidio-no-ruanda-30-anos-depois/
https://www.portaldeangola.com/benin-quer-supressao-de-vistos-com-angola/
https://www.portaldeangola.com/irao-ameaca-atacar-embaixadas-israelitas/
https://www.portaldeangola.com/assembleia-nacional-debate-proposta-de-lei-sobre-combate-a-actividade-mineira-ilegal/
https://www.portaldeangola.com/brasil-governo-de-lula-a-procura-de-consenso-sobre-o-defice-orcamental-e-o-aumento-da-despesa/
https://www.portaldeangola.com/zimbabue-lanca-nova-moeda-para-por-fim-a-anos-de-turbulencia-monetaria-e-crise-economica/
https://www.portaldeangola.com/estados-unidos-e-china-concordam-em-iniciar-negociacoes-sobre-o-crescimento-economico-global-equilibrado/
https://www.portaldeangola.com/mudanca-de-tom-de-biden-sobre-israel-timida-para-os-democratas-exagerada-para-os-republicanos/
https://www.portaldeangola.com/presidente-do-peru-diz-que-supostos-relogios-nao-declarados-eram-emprestados/
https://www.portaldeangola.com/china-usa-ia-para-semear-divisao-nos-eua-e-em-outros-paises-aponta-microsoft/
https://www.portaldeangola.com/acordo-mercosul-ue-inspira-cuidados-e-principal-obstaculo-e-a-franca-diz-haddad/
https://www.portaldeangola.com/tribunal-constitucional-declara-inconstitucional-sentenca-do-caso-500-milhoes-e-devolve-a-ao-tribunal-superior/
https://www.portaldeangola.com/emprego-permanece-solido-nos-eua-mercado-olha-com-expectativa-para-o-fed/
https://www.portaldeangola.com/tesla-descarta-plano-de-carro-de-baixo-custo-em-meio-a-acirrada-concorrencia-chinesa/
https://www.portaldeangola.com/nova-iorque-sacudida-por-terramoto-de-48-na-escala-de-richter-o-maior-em-mais-de-40-anos/
https://www.portaldeangola.com/ua-angola-condena-violencia-motivada-pelo-odio/
https://www.portaldeangola.com/angola-empenhada-no-desenvolvimento-do-programa-espacial-africano/
https://www.portaldeangola.com/petroleo-brent-dispara-acima-de-us-90-enquanto-emirados-arabes-unidos-ameacam-cortar-lacos-diplomaticos-com-israel/
https://www.portaldeangola.com/a-america-do-sul-podera-ultrapassar-a-africa-na-producao-de-cacau/
https://www.portaldeangola.com/rd-congo-obriga-as-multinacionais-do-sector-mineiro-a-aumentarem-o-conteudo-local-com-risco-de-perderem-contratos/
https://www.portaldeangola.com/novo-presidente-do-senegal-anuncia-auditoria-as-industrias-petrolifera-e-mineira/
https://www.portaldeangola.com/banco-central-do-quenia-quer-requisitos-de-capital-mais-elevados-para-os-bancos-enquanto-promove-a-expansao-regional/
https://www.portaldeangola.com/75-anos-da-nato-ucrania-foi-a-festa-em-bruxelas-mas-levou-pedido-mais-misseis-patriot/
https://www.portaldeangola.com/africa-do-sul-ex-presidente-do-parlamento-detida-no-ambito-de-investigacao-de-corrupcao/
https://www.portaldeangola.com/paz-melhora-indicadores-de-educacao-e-empregabilidade-no-cuando-cubango/
https://www.portaldeangola.com/pr-aborda-desenvolvimento-espacial-com-empresas-francesas/
https://www.portaldeangola.com/eua-e-ue-divergem-sobre-o-futuro-dos-subsidios-aos-combustiveis-fosseis-nas-negociacoes-da-ocde/
https://www.portaldeangola.com/eua-biden-pode-sacrificar-a-transicao-energetica-em-troca-do-apoio-republicano-ao-pacote-de-ajuda-a-ucrania/
https://www.portaldeangola.com/mercado-de-petroleo-devera-apertar-enquanto-opep-persiste-com-cortes-de-producao/
https://www.portaldeangola.com/eua-e-ue-podem-nao-chegar-a-acordo-sobre-minerais-criticos-esta-semana/
https://www.portaldeangola.com/a-economia-europeia-da-zona-euro-a-duas-velocidades-com-os-paises-do-sul-a-frente/
https://www.portaldeangola.com/sobe-para-nove-o-numero-de-mortos-no-sismo-em-taiwan-mais-de-700-feridos-e-dezenas-sob-escombros/
https://www.portaldeangola.com/julgamento-de-manuel-chang-nos-eua-marcado-para-29-de-julho-em-brooklin/
https://www.portaldeangola.com/angola-e-eau-estabelecem-cooperacao-em-materia-penal/
https://www.portaldeangola.com/andebol-seleccao-feminina-ja-completa-para-a-semana-da-ihf/
https://www.portaldeangola.com/o-que-o-comercio-financiamento-do-desenvolvimento-e-ide-revelam-sobre-as-relacoes-economicas-china-africa/
https://www.portaldeangola.com/manifestantes-em-jerusalem-chamam-netanyahu-de-traidor-e-pedem-eleicoes-ja-em-israel/
https://www.portaldeangola.com/o-uniforme-da-selecao-alema-de-futebol-proibido-por-semelhanca-com-simbologia-nazista/
https://www.portaldeangola.com/incendio-em-discoteca-de-istambul-faz-pelo-menos-27-mortos/
https://www.portaldeangola.com/novo-governo-em-portugal-relacoes-com-palop-nao-devem-mudar/
https://www.portaldeangola.com/senegal-novo-presidente-apela-a-mais-solidariedade-em-africa-contra-a-inseguranca/
https://www.portaldeangola.com/acto-central-do-dia-da-paz-e-reconciliacao-nacional-acontece-no-huambo/
https://www.portaldeangola.com/estrategia-espacial-nacional-2016-2025-com-resultados-concretos/
https://www.portaldeangola.com/ataque-israelita-destroi-consulado-iraniano-em-damasco-e-mata-alta-patente-militar/
https://www.portaldeangola.com/tera-a-aima-competencia-para-decretar-o-fim-do-visto-cplp/
https://www.portaldeangola.com/casas-a-venda-por-e1-em-patrica-e-ninguem-as-quer-comprar/
https://www.portaldeangola.com/falta-de-divisas-impede-operadores-economicos-sao-tomenses-de-abastecerem-o-mercado/
https://www.portaldeangola.com/pacote-legislativo-autarquico-ja-esta-no-parlamento/
https://www.portaldeangola.com/newspace-africa-atrai-principais-agencias-espaciais-do-mundo/
https://www.portaldeangola.com/turistas-encantados-com-as-potencialidades-historicas-de-mbanza-kongo/
https://www.portaldeangola.com/como-ficou-o-hospital-al-shifa-em-gaza-apos-duas-semanas-de-incursoes-israelitas/
https://www.portaldeangola.com/investigacao-jornalistica-liga-russia-a-doenca-que-afeta-diplomatas-dos-estados-unidos/
https://www.portaldeangola.com/mocambique-possivel-saida-da-samim-de-cabo-delgado-inquieta-sociedade-civil/
https://www.portaldeangola.com/mali-mais-de-80-partidos-e-organizacoes-apelam-a-eleicoes/
https://www.portaldeangola.com/escritora-paulina-chiziane-defende-uniao-e-reforco-de-parcerias/
https://www.portaldeangola.com/angola-dispoe-de-153-bilioes-de-kwanzas-para-investidores/
https://www.portaldeangola.com/barreiras-comerciais-entre-reino-unido-e-canada-aumentarao-devido-a-falta-de-acordo/
https://www.portaldeangola.com/india-retomara-restricoes-as-importacoes-de-energia-solar-para-impulsionar-os-produtores-locais/
https://www.portaldeangola.com/fornecedores-de-petroleo-dos-eua-penetram-em-mercados-outrora-dominados-pela-opep/
https://www.portaldeangola.com/nippon-steel-do-japao-diz-que-acordo-fortalecera-a-siderurgia-dos-eua-enquanto-biden-se-manifesta-contra-a-aquisicao/
https://www.portaldeangola.com/atividade-industrial-na-china-expande-pela-primeira-vez-em-seis-meses/
https://www.portaldeangola.com/depois-de-critica-de-lula-venezuela-pede-reuniao-a-governo-brasileiro/
https://www.portaldeangola.com/cristaos-de-todo-o-mundo-celebram-a-sexta-feira-santa/
https://www.portaldeangola.com/angola-obtem-primeira-vitoria-em-montreux/
https://www.portaldeangola.com/nacionalistas-homenageiam-antigos-presidentes-da-republica/
https://www.portaldeangola.com/salvador-475-anos-por-que-cidade-foi-escolhida-para-ser-1a-capital-do-brasil/
https://www.portaldeangola.com/politica-e-crime-as-ligacoes-perigosas-por-tras-do-assassinato-de-marielle-franco/
https://www.portaldeangola.com/ataques-russos-com-misseis-e-drones-atingem-centrais-termoeletricas-no-leste-da-ucrania/
https://www.portaldeangola.com/africa-do-sul-jacob-zuma-escapa-ileso-de-acidente-de-viacao/
https://www.portaldeangola.com/africa-do-sul-zuma-impedido-de-participar-nas-eleicoes-de-maio/
https://www.portaldeangola.com/arabia-saudita-o-maior-exortador-de-petroleo-visa-vendas-de-titulos-verdes-para-projetos-ecologicos/
https://www.portaldeangola.com/a-china-esta-a-comprar-mais-produtos-agricolas-de-africa-mas-ainda-ha-muito-espaco-para-crescimento/
https://www.portaldeangola.com/com-o-brent-a-ultrapassar-o-limiar-dos-87-dolares-por-barril-analistas-ja-preveem-precos-de-tres-digitos/
https://www.portaldeangola.com/a-captura-e-armazenamento-de-co2-no-sudeste-asiatico-esta-a-tornar-se-num-negocio-multibilionario-para-as-grandes-petroliferas/
https://www.portaldeangola.com/mentiras-sobre-brigitte-macron-ultrapassam-fronteiras-da-franca/
https://www.portaldeangola.com/obama-e-biden-uma-relacao-amistosa-com-pros-e-contras/
https://www.portaldeangola.com/comandante-polaco-do-eurocorps-demitido-por-suspeita-de-colaboracao-com-a-russia/
https://www.portaldeangola.com/presidente-da-republica-nomeia-ministro-do-turismo/
https://www.portaldeangola.com/minjud-quer-criar-bolsa-nacional-de-formadores-em-gestao-e-lideranca-juvenil/
https://www.portaldeangola.com/secretaria-do-tesouro-dos-eua-diz-que-o-crescimento-industrial-subsidiado-da-china-esta-a-distorcer-a-economia-mundial/
https://www.portaldeangola.com/ue-chega-a-acordo-para-prolongar-o-comercio-livre-de-tarifas-com-a-ucrania/
https://www.portaldeangola.com/japao-aumenta-ameaca-de-intervencao-a-medida-que-o-iene-atinge-o-nivel-mais-baixo-desde-1990/
https://www.portaldeangola.com/a-refinaria-de-petroleo-dangote-na-nigeria-podera-acelerar-o-declinio-do-sector-europeu/
https://www.portaldeangola.com/banco-africano-de-energia-especializado-no-financiamento-de-combustiveis-fosseis-devera-comecar-este-ano/
https://www.portaldeangola.com/brasil-e-franca-lancam-programa-de-investimento-de-1-bilhoes-de-euros-para-a-floresta-amazonica/
https://www.portaldeangola.com/nao-devemos-desistir-da-democracia-eu-nao-desisto-aguiar-branco-fala-finalmente-como-presidente-da-ar/
https://www.portaldeangola.com/general-do-niger-discute-cooperacao-em-materia-de-seguranca-com-putin/
https://www.portaldeangola.com/angola-ratifica-protocolo-sobre-emprego-e-trabalho-da-sadc/
https://www.portaldeangola.com/a18-pro-revoluciona-iphone-16-pro-com-inteligencia-artificial-inedita/
https://www.portaldeangola.com/a-eliminacao-progressiva-do-carvao-o-combustivel-fossil-mais-sujo-esta-a-revelar-se-mais-desafiadora-do-que-o-previsto/
https://www.portaldeangola.com/preco-do-cacau-bate-terca-feira-recorde-historico-de-10-mil-dolares-por-tonelada/
https://www.portaldeangola.com/china-continuara-a-cooperar-na-reestruturacao-da-divida-da-zambia-diz-autoridade-chinesa-sem-dar-detalhes/
https://www.portaldeangola.com/gana-procura-acelerar-negociacoes-de-reestruturacao-da-divida/
https://www.portaldeangola.com/angola-africa-global-logistics-quer-desenvolver-volume-de-negocios-ao-longo-do-corredor-do-lobito/
https://www.portaldeangola.com/portugal-psd-retira-nome-de-aguiar-branco-para-presidente-do-parlamento/
https://www.portaldeangola.com/governo-quer-contratacao-publica-em-conformidade-com-a-sustentabilidade/
https://www.portaldeangola.com/a-ferramenta-de-ia-capaz-de-detectar-tumores-que-passaram-despercebidos-por-medicos/
https://www.portaldeangola.com/israel-se-irrita-com-abstencao-dos-eua-em-votacao-na-onu-sobre-cessar-fogo-em-gaza/
https://www.portaldeangola.com/em-meio-a-lagrimas-vinicius-junior-diz-que-ofensas-racistas-na-espanha-estao-tirando-sua-alegria-de-jogar/
https://www.portaldeangola.com/itamaraty-convoca-embaixador-da-hungria-para-explicar-hospedagem-de-bolsonaro-apos-apreensao-de-passaporte/
https://www.portaldeangola.com/ataque-de-moscovo-numero-de-mortos-sobe-para-139-detidos-mais-tres-suspeitos/
https://www.portaldeangola.com/ha-200-anos-brasil-ganhava-sua-primeira-constituicao/
https://www.portaldeangola.com/tribunal-supremo-ouve-declarantes-no-julgamento-do-antigo-embaixador-na-etiopia/
https://www.portaldeangola.com/conselho-de-seguranca-da-onu-exige-cessar-fogo-em-gaza/
https://www.portaldeangola.com/candidatos-a-presidencia-do-senegal-cumprimentam-adversario-antissistema-por-vitoria/
https://www.portaldeangola.com/fmi-pede-a-china-reformas-que-favorecam-o-mercado/
https://www.portaldeangola.com/reuniao-extraodinaria-da-dupla-troika-da-sadc-marca-semana/
https://www.portaldeangola.com/guine-bissau-cidadaos-criam-frente-popular-para-salvar-a-democracia/
https://www.portaldeangola.com/seleccao-angolana-de-futebol-considerada-mais-madura-apos-o-can/"""
direct_URLs = text.split('\n')
final_result = direct_URLs.copy()
# final_result = final_result[3383:]
print(len(final_result))

url_count = 0
processed_url_count = 0
source = 'portaldeangola.com'
for url in final_result:
    if url:
        print(url, "FINE")
        ## SCRAPING USING NEWSPLEASE:
        try:
            header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
            response = requests.get(url, headers=header)
            # process
            article = NewsPlease.from_html(response.text, url=url).__dict__
            # add on some extras
            article['date_download']=datetime.now()
            article['download_via'] = "Direct2"
            article['source_domain'] = source
            # title has no problem
            
            
            # custom parser
            soup = BeautifulSoup(response.content, 'html.parser')
            
            try:
                category = soup.find_all('a', {'class' :'tdb-entry-crumb'})[-1].text.strip()
            except:
                category = 'News'
            print(category)
            if category in ['Opinião', 'Ciências e Tecnologia', 'CMaisinema', 'Cultura', 'Vida', 'Ciência & Tecnologia', 'Desporto']:
                article['title'] = 'From uninterested category'
                article['date_publish'] = None
                article['maintext'] = None
                print(article['title'], category)
                
            else:
                try:
                    date = soup.find('meta', {'itemprop' : "datePublished"})['content']
                    article['date_publish'] = dateparser.parse(date).replace(tzinfo=None)
                except:
                    article['date_publish'] = article['date_publish'] 
                print("newsplease date: ",  article['date_publish'])
                
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
 
    else:
        pass

print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")
