 
import os
import json
from urllib.parse import urlparse
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables from .env
load_dotenv()

# Settings from .env
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "visual_product_matcher")
MONGO_COL = os.getenv("MONGO_COL", "products")
JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "uploaded_urls.json")  

# Connect to MongoDB Atlas
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
col = db[MONGO_COL]

# Category inference from URL path
def infer_category(url):
    parts = urlparse(url).path.split('/')
    for subcat in ["cars", "fruits", "phone", "softdrink", "tshirts"]:
        if subcat in parts:
            return subcat
    return "unknown"

# Name formatting from file name
def format_name(filename):
    base = os.path.splitext(filename)[0]    
    base = base.replace("_", " ")           
    base = base.replace("-", " ")           
    return base.title()

def main():
    # Load items from JSON
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        items = json.load(f)

    inserted_count = 0
    for item in items:
        name = format_name(item["file"])
        category = infer_category(item["url"])
        url = item["url"]
        doc = {
            "name": name,
            "category": category,
            "url": url,
            "embedding": None   
        }

       
        if col.count_documents({"url": url}, limit = 1) == 0:
            col.insert_one(doc)
            print(f"Inserted: {name} | {category}")
            inserted_count += 1
        else:
            print(f"Skipped (already exists): {name}")

    print(f"\nSeeded {inserted_count} products to MongoDB '{MONGO_DB}.{MONGO_COL}'.")

if __name__ == "__main__":
    main()
