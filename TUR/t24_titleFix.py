import pandas as pd
from pymongo import MongoClient
import urllib
import os
import re


db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p



def modify_titles(col_name, source_domains):
    cursor = db[col_name].find(
        {
            #'include' : True,
            'source_domain' : source_domains
            #'source_domain' : {'$in' : source_domains},
            #'maintext' : {'$nin' : ['', None]},
            #'maintext_translated' : {'$nin' : ['', None]},
            #'maintext': { '$regex': '^[\s\S]{20000,}$' },
        }
    )
    for doc in cursor:
        #print('Previous:', doc['title'])
        db[col_name].update_one(
            {'_id': doc['_id']},
            {
                '$set':{
                    #'title': re.sub('\(1\)', '', doc['title'])
                    # 'title': re.sub('\(2\)', '', doc['title']),
                    # 'title': re.sub('\(3\)', '', doc['title']),
                    # 'title': re.sub('\(4\)', '', doc['title']),
                     #'title': re.sub('\(5\)', '', doc['title']),
                    # 'title': re.sub('\(6\)', '', doc['title']),
                    #'title': re.sub('\(7\)', '', doc['title']),
                    # 'title': re.sub('\(8\)', '', doc['title']),
                    # 'title': re.sub('\(9\)', '', doc['title']),
                    # 'title': re.sub('- 1', '', doc['title']),
                    # 'title': re.sub('- 2', '', doc['title']),
                    # 'title': re.sub('- 3', '', doc['title']),
                    #'title': re.sub('- 4', '', doc['title']),
                    # 'title': re.sub('- 5', '', doc['title']),
                    # 'title': re.sub('- 6', '', doc['title']),
                    # 'title': re.sub('- 7', '', doc['title']),
                    # 'title': re.sub('- 8', '', doc['title']),
                    # 'title': re.sub('- 9', '', doc['title']),
                    # 'title': re.sub('\(FOTOĞRAFLAR\)', '', doc['title']),
                    # 'title': re.sub('/ Ek fotoğraflar', '', doc['title']),
                    'title' : doc['title'].strip(),
                    #'title' : re.sub('\(aktüel görüntü 2 \)', '', doc['title']) 
                    #'title' : re.sub('\(Aktüel Görüntü\)', '', doc['title']) 
                    #'title' : re.sub('\(aktüel görüntü\)', '', doc['title'])  
                    #'title' : re.sub('\(ek bilgilerle\)-', '', doc['title'])  
                    #'title' : re.sub('\(Ek fotoğraflar \) -', '', doc['title'])
                    #'title' : re.sub('\(ek fotoğraflar\)', '', doc['title'])   
                    #'title' : re.sub('\(EK GÖRÜNTÜLERLE\)', '', doc['title'])
                    #'title' : re.sub('\(Görüntülü Haber\)', '', doc['title'])
                    #'title' : re.sub('\(aktüel görüntüler\)-', '', doc['title'])
                    #'title' : re.sub('\(aktüel görüntülerle geniş haber\) -', '', doc['title'])
                    #'title' : re.sub('\(Aktüel görüntülerle geniş haber\)', '', doc['title'])
                    #'title' : re.sub('\(aktüel görüntülerle geniş haber\)-', '', doc['title'])
                    #'title' : re.sub('\(aktüel görüntülerle\)', '', doc['title'])
                    #'title' : re.sub('\(aktüel görüntüyle\)-', '', doc['title'])
                    #'title' : re.sub('\(Arşiv Görüntü\)', '', doc['title'])
                    #'title' : re.sub('\(Düzelterek yeniden\) -', '', doc['title'])
                    #'title' : re.sub('\(ek bilgi ve fotoğrafla\)', '', doc['title'])
                    #'title' : re.sub('\(Ek bilgi ve fotoğraflarla\) -', '', doc['title'])
                    #'title' : re.sub('\(ek bilgi ve görüntü\)', '', doc['title'])
                    #'title' : re.sub('\(ek bilgi ve görüntülerle geniş haber\)', '', doc['title'])
                  #'title' : re.sub('\(ek bilgi ve görüntülerle\)', '', doc['title'])
                  #'title' : re.sub('\(Ek bilgi ve görüntülerle\)', '', doc['title'])
                  #'title' : re.sub('\(EK BİLGİ VE GÖRÜNTÜLERLE\)', '', doc['title'])
                  #'title' : re.sub('\(ek bilgilerle yeniden\)', '', doc['title'])
                  #'title' : re.sub('\(Ek bilgilerle\)  -', '', doc['title'])
                  #'title' : re.sub('\(ek bilgilerle\)-', '', doc['title'])
                  #'title' : re.sub('\(Ek bilgilerle\)', '', doc['title'])
                  #'title' : re.sub('\(ek bilgiyle\)', '', doc['title'])
                  #'title' : re.sub('\(EK BİLGİYLE\) -', '', doc['title'])
                  #'title' : re.sub('\(ek fotoğraflar\)', '', doc['title'])
                  #'title' : re.sub('\(Ek fotoğraflar\) -', '', doc['title'])
                  #'title' : re.sub('\(ek fotoğraflar\)', '', doc['title'])
                  #'title' : re.sub('\(Geniş haber\)  -', '', doc['title'])
                  #'title' : re.sub('\(geniş haber\)', '', doc['title'])
                  #'title' : re.sub('\(geniş haber\) -', '', doc['title'])
                  #'title' : re.sub('\(Geniş haber\)', '', doc['title'])
                  #'title' : re.sub('Ek fotoğraflar //', '', doc['title'])
                  #'title' : re.sub('\(GENİŞ HABER\)', '', doc['title'])
                  #'title' : re.sub('\(GENİŞ\)', '', doc['title'])
                  #'title' : re.sub('\(Geniş\)', '', doc['title'])
                  #'title' : re.sub('\(Görüntülerle\)', '', doc['title'])
                  #'title' : re.sub('\(Görüntülü  Haber\)', '', doc['title'])
                  #'title' : re.sub('\(Havadan Görüntülerle\)', '', doc['title'])
                  #'title' : re.sub('\(ÖZEL\) -', '', doc['title'])
                  #'title' : re.sub('\(ÖZEL\)', '', doc['title'])
                  #'title' : re.sub('\(ÖZEL\)-', '', doc['title'])
                  #'title' : re.sub('\(yeniden\) -', '', doc['title'])
                  #'title' : re.sub('\(YENİDEN\) -', '', doc['title'])
                 # 'title' : re.sub('\(YENİDEN\)', '', doc['title'])


                    
                }
            }

        )
        #print('Updated:', doc['title'])



for year in range(2012, 2023):
    for month in range(1, 13):
        year_month = str(year)+'-'+str(month)
        print('In:', year_month)
        colname = 'articles-' + year_month
        modify_titles(colname, 't24.com.tr')   

        







     


