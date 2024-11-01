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
        db[col_name].update_one(
            {'_id': doc['_id']},
            {
                '$set':{
                    'maintext': re.sub('\| Graphic NewsPLUS App \|Download our Graphic NewsPlus App and follow us on Facebook, and Twitter for more.', '', doc['maintext']),

                    #'maintext': re.sub('\|\|.', '', doc['maintext'])
                }
            }

        )
        print('Updated:', doc['_id'])


modify_titles('articles-2023-4', 'graphic.com.gh')        




