from bs4 import BeautifulSoup
import requests
import pandas as pd
import random
import os
import sys
sys.setrecursionlimit(10000)

header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}



# lists
urls = pd.read_excel('/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/PER/larepublica_35500.xlsx')
urls2 = pd.read_excel('/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/PER/larepublica2_50100.xlsx')
urls3 = pd.read_excel('/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/PER/larepublica3_90000.xlsx')
urls4 = pd.read_excel('/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/PER/larepublica4_178000.xlsx')
urls5 = pd.read_excel('/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/PER/larepublica5_368700.xlsx')
urls6 = pd.read_csv('/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/PER/larepublica5_398200.csv')


urls = pd.concat([urls, urls2, urls3, urls4, urls5, urls6], ignore_index = True)

urls=list(urls['url'])
print(len(urls))
   
# function created
def scrape(site):
       
    # getting the request from url
    r = requests.get(site, headers = header)
       
    # converting the text
    s = BeautifulSoup(r.text,"html.parser")
       
    for i in s.find_all("a"):
          
        href = i.attrs['href']

           
        if 'https://larepublica.pe' in href:

            if '/tag/' not in href:
                
                if 'https://api.whatsapp.com/' not in href:

                    if 'https://www.facebook.com/sharer' not in href:

                        if 'https://twitter.com/intent/' not in href:

                            if len(href.split('/')) > 5:
                    
                                if href not in  urls:

                                    urls.append(href) 

                                    #print(href)
                                    print('NOW URLS', len(urls))

                                    if len(urls) % 100 == 0 and len(urls)!= 0:

                                        data_prev = '/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/PER/larepublica5_' + str(len(urls)-100) + '.csv'
                                        print('DELETING PREVIOUS FILE:', data_prev)

                                        if len(urls) - 100 != 0:

                                            try:
                                            
                                                os.remove(data_prev)

                                            except:
                                                pass

                                        print('SAVING NEW FILE')

                                        url_data = pd.DataFrame()

                                        url_data['url'] = urls
                                        dataname = '/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/PER/larepublica5_' + str(len(urls)) + '.csv'

                                        url_data.to_csv(dataname)

                                        # calling it self
                                    try:
                                        scrape(href)
                                    except:
                                        # randomly select another href
                                        scrape(random.choice(urls))




# randomly start with some url
scrape('https://larepublica.pe')

#url = 'https://larepublica.pe/politica/congreso/2023/04/10/congreso-fiebre-de-creacion-de-nuevas-universidades-publicas-peruanas-ministerio-de-educacion-rosendo-serna-870690'



