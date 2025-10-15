from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from typing import List, Optional
from bson import ObjectId

class MongoDB:
    client: AsyncIOMotorClient = None
    
    @classmethod
    def connect(cls):
        # Simple connection with TLS options in connection string
        cls.client = AsyncIOMotorClient(
            settings.mongo_uri,
            tlsAllowInvalidCertificates=True
        )
        
    @classmethod
    def close(cls):
        if cls.client:
            cls.client.close()
    
    @classmethod
    def get_collection(cls):
        db = cls.client[settings.mongo_db]
        return db[settings.mongo_col]

async def get_products(
    category: Optional[str] = None,
    limit: int = 20,
    skip: int = 0,
    require_embedding: bool = False
) -> List[dict]:
    col = MongoDB.get_collection()
    filter_query = {}
    
    if category:
        filter_query["category"] = category
    
    if require_embedding:
        filter_query["embedding"] = {"$exists": True, "$ne": None}
    
    cursor = col.find(filter_query).skip(skip).limit(limit)
    products = []
    
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        products.append(doc)
    
    return products

async def get_product_by_id(product_id: str) -> Optional[dict]:
    col = MongoDB.get_collection()
    try:
        doc = await col.find_one({"_id": ObjectId(product_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc
    except:
        return None

async def get_all_embeddings() -> List[dict]:
    """Get all products that have embeddings for similarity search"""
    col = MongoDB.get_collection()
    cursor = col.find({"embedding": {"$exists": True, "$ne": None}})
    
    products = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        products.append(doc)
    
    return products
