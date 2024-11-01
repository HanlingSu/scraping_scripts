import pandas as pd
from pymongo import MongoClient
import urllib
import os


db = MongoClient('mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true').ml4p



## This script has some queries for the db which can be used/modified depending on the need




## This one queries dailynew.co.tz articles only in the deleted-articles collection. The collection names can be found in collections.csv folder. The format of the regular collections is as follows: articles-YYYY-MM. Example: articles-2014-10, articles-2014-3
## You can uncomment if you want to query only violencenonlethal categories for instance.

cursor = db['articles-2022-12'].find(
    {
      #'event_type': 'violencenonlethal', 
      'source_domain': 'ojo-publico.com'
    }
)

## If you want to save your query as a data frame, just run the following lines after setting your cursor. You will need these three lines after setting your cursor settings.

all_docs = [_doc for _doc in cursor]
df = pd.DataFrame(all_docs)
df.to_excel('/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/ojopublico_dec22.xlsx')
