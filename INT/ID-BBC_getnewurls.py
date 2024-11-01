import requests
from bs4 import BeautifulSoup
from newsplease import NewsPlease
from datetime import datetime

# Headers for scraping
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# List of sitemap URLs (manually provided by you)
sitemap_urls = [
    "https://www.bbc.com/sitemaps/https-sitemap-com-news-1.xml",
    "https://www.bbc.com/sitemaps/https-sitemap-com-news-2.xml",
    "https://www.bbc.com/sitemaps/https-sitemap-com-news-3.xml"
]

# List to store article URLs
article_urls = []

# Step 1: Extract article URLs from the provided sitemaps
for sitemap_url in sitemap_urls:
    print(f"Extracting from: {sitemap_url}")
    response = requests.get(sitemap_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Collect all <loc> tags, which contain the article URLs
    for loc_tag in soup.findAll('loc'):
        article_urls.append(loc_tag.text)

print(f"Total number of article URLs found: {len(article_urls)}")

# Step 2: Process and scrape each article URL
for url in article_urls:
    if not url or "bbc.com" not in url:
        continue

    print(f"Processing: {url}")
    
    try:
        # Scraping article using NewsPlease
        response = requests.get(url, headers=headers)
        article = NewsPlease.from_html(response.text, url=url).__dict__
        
        # Print article details (instead of inserting into MongoDB)
        print("\n=== Article Details ===")
        print(f"URL: {article.get('url', 'N/A')}")
        print(f"Title: {article.get('title', 'N/A')}")
        print(f"Publication Date: {article.get('date_publish', 'N/A')}")
        print(f"Main Text: {article.get('maintext', 'N/A')[:500]}...")  # Print first 500 chars of main text
        print("======================\n")
    
    except Exception as err:
        print(f"Error processing {url}: {err}")

print(f"Done processing {len(article_urls)} articles.")

## INSERTING IN THE DB:
url_count = 0
for url in list_urls:
    if url == "":
        pass
    else:
        if url == None:
            pass
        else:
            if "bbc.com" in url:
                print(url, "FINE")
                ## SCRAPING USING NEWSPLEASE:
                try:
                    #header = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36''(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36')}
                    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                    response = requests.get(url, headers=header)
                    # process
                    article = NewsPlease.from_html(response.text, url=url).__dict__
                    # add on some extras
                    article['date_download']=datetime.now()
                    article['download_via'] = "Direct2"
                    
                    ## Fixing main texts when needed:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Get Main Text:
                    if article['maintext'] == None:
                        try:
                            soup.find('div', {'aria-live' : "polite"}).find_all('p')
                            maintext = ""
                            for i in  soup.find('div', {'aria-live' : "polite"}).find_all('p'):
                                maintext += i.text
                            article['maintext'] = maintext
                        except:
                            try:
                                soup.find('main', {'role':'main'}).find_all('p')
                                maintext = ""
                                for i in soup.find('main', {'role':'main'}).find_all('p'):
                                    maintext += i.text
                                article['maintext'] = maintext
                            except:
                                try:
                                    soup.find_all('div', {'data-component': "text-block"})
                                    maintext = ""
                                    for i in soup.find_all('div', {'data-component' : "text-block"}):
                                        maintext+= i.find('p').text
                                    article['maintext'] = maintext
                                except:
                                    try:
                                        soup.find_all('p', {'class' : "ssrcss-1q0x1qg-Paragraph eq5iqo00"})
                                        maintext = ""
                                        for i in soup.find_all('p', {'class' : "ssrcss-1q0x1qg-Paragraph eq5iqo00"}):
                                            maintext+= i.text
                                        article['maintext'] = maintext
                                    except:
                                        maintext = None
                                        article['maintext'] = None

                    #try:
                    #    contains_date = soup.find("div", {"class":"post-meta-date"}).text
                        #contains_date = soup.find("i", {"class":"fa fa-calendar"}).text
                    #    article_date = dateparser.parse(contains_date, date_formats=['%d/%m/%Y'])
                    #    article['date_publish'] = article_date
                    #except:
                    #    article_date = article['date_publish']
                    #    article['date_publish'] = article_date

                    ## Inserting into the db
                    try:
                        year = article['date_publish'].year
                        month = article['date_publish'].month
                        colname = f'articles-{year}-{month}'
                        #print(article)
                    except:
                        colname = 'articles-nodate'
                    try:
                        #TEMP: deleting the stuff i included with the wrong domain:
                        #myquery = { "url": final_url, "source_domain" : 'web.archive.org'}
                        #db[colname].delete_one(myquery)
                        # Inserting article into the db:
                        db[colname].insert_one(article)
                        # count:
                        url_count = url_count + 1
                        #print(article['date_publish'].month)
                        #print(article['title'][0:200])
                        #print(article['maintext'][0:200])
                        print("Inserted! in ", colname, " - number of urls so far: ", url_count)
                        db['urls'].insert_one({'url': article['url']})
                    except DuplicateKeyError:
                        print("DUPLICATE! Not inserted.")
                except Exception as err: 
                    print("ERRORRRR......", err)
                    pass
            else:
                pass


print("Done inserting ", url_count, " manually collected urls from ",  source, " into the db.")