from pymongo import MongoClient

# Database connection
MONGO_URI = "mongodb://zungru:balsas.rial.tanoaks.schmoe.coffing@db-wibbels.sas.upenn.edu/?authSource=ml4p&tls=true"
db = MongoClient(MONGO_URI).ml4p

# Define the collections to check
collections = {
    "December 2024": "articles-2024-12",
    "February 2025": "articles-2025-2",
    "March 2025": "articles-2025-3"
}

def count_urls_for_source(source_domain):
    """Count the number of articles from a specific source in each month's collection."""
    for month, collection_name in collections.items():
        try:
            count = db[collection_name].count_documents({"source_domain": source_domain})
            print(f"{month}: {count} articles found from {source_domain}.")
        except Exception as e:
            print(f"Error accessing {collection_name}: {e}")

if __name__ == "__main__":
    source = "asiatimes.com"  # Specify the source
    count_urls_for_source(source)
