import requests
import json
from gdeltdoc import GdeltDoc, Filters
import pandas as pd
import time
import re



final_URLs = pd.Series()
gd = GdeltDoc()

for year in range(2020, 2024):
    for month in range(1, 13):
        if month < 10:
            month_str = '0' + str(month)
        else:
            month_str =  str(month)
        for day in range(1, 32):
            day_end = day+1
            if day < 10:
                day_str = '0' + str(day)
            else:
                day_str =  str(day)
            if day_end < 10:
                day_end_str = '0' + str(day_end)
            else:
                day_end_str =  str(day_end)
            date_start = str(year) + '-' + month_str + '-' + day_str
            date_end = str(year) + '-' + month_str + '-' + day_end_str
            print(date_start)
            f = Filters(
                start_date = date_start,
                end_date = date_end,
                num_records = 250,
                domain = "jugantor.com",
            )

            # Search for articles matching the filters
            articles = gd.article_search(f)
            try:

                final_URLs = final_URLs.append(articles['url'], ignore_index=True)
                final_URLs = final_URLs.drop_duplicates()
                time.sleep(5)

            except:
                pass

            print(len(final_URLs))

        final_URLs.to_csv('/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/BGD/wayback/gdelt_jugantor.csv', index=False, header=False)

# Get a timeline of the number of articles matching the filters
# timeline = gd.timeline_search("timelinevol", f)