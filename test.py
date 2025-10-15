import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
try:
    print(client.list_database_names())
    print("Successfully connected to MongoDB Atlas.")
except Exception as e:
    print("Connection error:", e)
