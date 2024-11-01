#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 24 13:23:19 2021
"""

#import pymongo
#pymongo.version
import os
import getpass
from dateutil.relativedelta import relativedelta
import pandas as pd
import plotly.express as px
from tqdm import tqdm
import pymongo
from pymongo import MongoClient
pymongo.version
import urllib.parse


uri = 'mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true'

db = MongoClient(uri).ml4p


def graph_counts(domain, include=True):
    dates = pd.date_range(start='2012-1-1', end=pd.Timestamp.today()+relativedelta(months=1), freq='m')
    #dates = pd.date_range(start='2012-1-1', end='2021-9-1', freq='m')
    
    counts = []

    for date in tqdm(dates):

        if include:
            count = db[f'articles-{date.year}-{date.month}'].count_documents(
                {
                    'source_domain': domain,
                    #'download_via': "Direct2",
                    #'include': True
                }
            )
        else:
            count = db[f'articles-{date.year}-{date.month}'].count_documents(
                {
                    'source_domain': domain,
                    #'download_via': "Direct2"
                }
            )            

        counts.append(count)


    df = pd.DataFrame({'date': dates, 'count': counts})
    fig = px.line(df, x="date", y="count", title=f'{domain} article count over time')
    fig.show()


def graph_counts_country(iso_code, include=True):
   
    doms = db['sources'].find({'primary_location': iso_code.upper(), 'include' : True})

    doms = [doc['source_domain'] for doc in doms]

    for dom in doms:
        graph_counts(dom, include=include)


graph_counts_country('PER')