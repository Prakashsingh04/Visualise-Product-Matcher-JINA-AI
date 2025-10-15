# scripts/check_embedding_dims.py
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB", "visual_product_matcher")]
col = db[os.getenv("MONGO_COL", "products")]

sample = col.find_one({"embedding": {"$exists": True, "$n   e": None}})
if sample:
    print(f"Database embedding dimensions: {len(sample['embedding'])}")
else:
    print("No embeddings found")
