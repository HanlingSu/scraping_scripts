import pandas as pd
from pymongo import MongoClient
import re
from bson.objectid import ObjectId
import os
import getpass
from dateutil.relativedelta import relativedelta
import pandas as pd
import os
from pathlib import Path
import re
import pandas as pd
import time
from dotenv import load_dotenv
from pymongo import MongoClient
import openpyxl
from datetime import datetime

db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p
today = pd.Timestamp.now()

df = pd.DataFrame()
df['date'] = pd.date_range('2012-1-1', today + pd.Timedelta(31, 'd') , freq='M')
df.index = df['date']
df['year'] = [dd.year for dd in df.index]
df['month'] = [dd.month for dd in df.index]
queue = []
print(df.index)


#docs=[]
for dt in df.index:
    count = 0
    colname = f'articles-{dt.year}-{dt.month}'
    cur = db[colname].find(
            {
                #'id': '60882a63f8bb748cadce4bf0'
                'source_domain': {'$in':['lesahel.org']},
                'maintext':{'$regex':'Spread the love\nSharing is caring!'}
                #'include': {'$exists':True},
                #'event_type_RAI':{'$exists':False}
                #'civic1.event_type':{'$exists':True},
                #'maintext_translated':{'$exists':False},
                
            #     'title': {
            #             '$exists': True,
            #             '$ne': '',
            #             '$ne': None,
            #             '$type': 'string'
            #         },
            #     'maintext': {
            #             '$exists': True,
            #             '$ne': '',
            #             '$ne': None,
            #             '$type': 'string'
            #         }
            }
        )
    docs = [doc for doc in cur]
    new_maintext = []
    #count+=db[colname].count()
    #string = '>>> To purchase a single copy of the issue click here'
    for doc in docs:
        new_maintext.append(doc['maintext'][77:])
        # if string in doc['maintext']:
        #     new_maintext.append(doc['maintext'].replace(string,""))
        #     count+=1
        # else:
        #     new_maintext.append(doc['maintext'])
    
    for i, doc in enumerate(docs):
        db[colname].update_one(
            {'_id':docs[i]['_id']},
            {
                '$set':
                {
                    'maintext':new_maintext[i]
                }

            }

        )
    print(colname,f'-------- deleted {len(docs)} data with the string')

for dt in df.index:
    count = 0
    colname = f'articles-{dt.year}-{dt.month}'
    cur = db[colname].find(
            {
                #'id': '60882a63f8bb748cadce4bf0'
                'source_domain': {'$in':['lesahel.org']},
                'maintext':{'$regex':'Partager vers les réseaux'}
                #'include': {'$exists':True},
                #'event_type_RAI':{'$exists':False}
                #'civic1.event_type':{'$exists':True},
                #'maintext_translated':{'$exists':False},
                
            #     'title': {
            #             '$exists': True,
            #             '$ne': '',
            #             '$ne': None,
            #             '$type': 'string'
            #         },
            #     'maintext': {
            #             '$exists': True,
            #             '$ne': '',
            #             '$ne': None,
            #             '$type': 'string'
            #         }
            }
        )
    docs = [doc for doc in cur]
    new_maintext = []
    #count+=db[colname].count()
    #string = '>>> To purchase a single copy of the issue click here'
    for doc in docs:
        new_maintext.append(doc['maintext'][26:])
        # if string in doc['maintext']:
        #     new_maintext.append(doc['maintext'].replace(string,""))
        #     count+=1
        # else:
        #     new_maintext.append(doc['maintext'])
    
    for i, doc in enumerate(docs):
        db[colname].update_one(
            {'_id':docs[i]['_id']},
            {
                '$set':
                {
                    'maintext':new_maintext[i]
                }

            }

        )
    print(colname,f'-------- deleted {len(docs)} data with the string')
