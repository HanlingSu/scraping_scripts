import pandas as pd
from pymongo import MongoClient
import urllib
import os
import re


db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p



def dedup_title_collection(colname, source_domains):
    cursor = db[colname].find({'source_domain': source_domains}, batch_size=1)
    mod_count = 0
    for _doc in cursor:
        try:
            cur = db[colname].find(
                {
                    'source_domain': _doc['source_domain'],
                    '_id':  _doc['_id'],
                    'title':  _doc['title'],
                }
            )
            for i in cur:
                try:
                    db['deleted-articles'].insert_one(i)
                except DuplicateKeyError:
                    pass
            res = db[colname].delete_many(
                {
                    'source_domain': _doc['source_domain'],
                    '_id': {'$ne': _doc['_id']},
                    'title':  _doc['title'],
                }
            )
            if res.deleted_count != 0:
                mod_count += res.deleted_count
        except:
            pass



for year in range(2012, 2023):
    for month in range(1, 13):
        year_month = str(year)+'-'+str(month)
        print('In:', year_month)
        colname = 'articles-' + year_month
        dedup_title_collection(colname, 't24.com.tr')   



