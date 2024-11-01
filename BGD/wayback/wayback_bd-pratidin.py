import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Function to create a session with retry logic
def create_session():
    session = requests.Session()
    retry = Retry(
        total=5,  # Total retries
        backoff_factor=1,  # Time to wait between retries
        status_forcelist=[500, 502, 503, 504]  # Retry on these HTTP status codes
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    return session

# Function to extract URLs from a webpage
def extract_urls_from_snapshot(session, snapshot_url):
    try:
        response = session.get(snapshot_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        soup = BeautifulSoup(response.content, "html.parser")
        urls = [a['href'] for a in soup.find_all('a', href=True)]
        return urls
    except requests.RequestException as e:
        print(f"Error fetching {snapshot_url}: {e}")
        return []


# Function to save URLs to a CSV file using pandas
def save_urls_to_csv(urls, file_name):
    df = pd.DataFrame(urls, columns=['URL'])
    df.to_csv(file_name, mode='a', index=False, header=not pd.io.common.file_exists(file_name))

# Define the URL and time range
url = "bd-pratidin.com"
from_date = "2022"
to_date = "2023"

# Query the Wayback Machine CDX API
response = requests.get(f"https://web.archive.org/cdx/search/cdx?url={url}&from={from_date}&to={to_date}&output=json")
data = response.json()

# Extract snapshot URLs
base_wayback_url = "https://web.archive.org/web/"
snapshot_urls = [f"{base_wayback_url}{entry[1]}/{entry[2]}" for entry in data[1:]]  # Skip the first entry (header)

# Create a session with retry logic
session = create_session()

# List to store URLs before writing to CSV
buffered_urls = []
batch_size = 100
file_name = '/home/mlp2/Downloads/peace-machine/peacemachine/getnewurls/BGD/wayback/wayback_bdpratidin2.csv'

# Process each snapshot URL
for i, snapshot_url in enumerate(snapshot_urls):
    urls = extract_urls_from_snapshot(session, snapshot_url)
    buffered_urls.extend(urls)
    buffered_urls = list(set(buffered_urls))
    print(f"Batch {i}: {len(buffered_urls)} URLs ... ")
    # Save to CSV in batches
    if (i + 1) % batch_size == 0:
        save_urls_to_csv(buffered_urls, file_name)
        print(f"Saved {i + 1} snapshot of {len(buffered_urls)} URLs to {file_name}")
        buffered_urls = []  # Clear the buffer

    time.sleep(3)  # Add a delay between requests to avoid rate limiting

# Save any remaining URLs in the buffer
if buffered_urls:
    save_urls_to_csv(buffered_urls, file_name)
    print(f"Saved remaining {len(buffered_urls)} URLs to {file_name}")

print("URL extraction and saving completed.")
