import os
import time
from dotenv import load_dotenv
from pymongo import MongoClient
import httpx

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "visual_product_matcher")
MONGO_COL = os.getenv("MONGO_COL", "products")
JINA_API_KEY = os.getenv("JINA_API_KEY", "")
JINA_ENDPOINT = "https://api.jina.ai/v1/embeddings"

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
col = db[MONGO_COL]

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {JINA_API_KEY}"
}

def get_embedding(image_url):
    """
    Get embedding for a single image URL using Jina CLIP v2
    """
    payload = {
        "model": "jina-clip-v2",
        "input": [
            {"image": image_url}
        ]
    }
    
    try:
        with httpx.Client(timeout=60.0) as http_client:
            response = http_client.post(JINA_ENDPOINT, json=payload, headers=headers)
        
        response.raise_for_status()
        data = response.json()
        
        # Parse response - Jina v1 embeddings API returns data in 'data' array
        if 'data' in data and len(data['data']) > 0:
            embedding = data['data'][0]['embedding']
            return embedding
        else:
            print(f"Unexpected response format: {data}")
            return None
            
    except httpx.HTTPStatusError as e:
        print(f"HTTP {e.response.status_code} error: {e.response.text[:200]}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    # Find all products without embeddings
    to_embed = list(col.find({"embedding": None}))
    print(f"Found {len(to_embed)} items without embeddings.\n")
    
    if len(to_embed) == 0:
        print("All products already have embeddings!")
        return
    
    total = len(to_embed)
    success_count = 0
    fail_count = 0

    for idx, prod in enumerate(to_embed, 1):
        url = prod.get("url")
        name = prod.get("name", "Unknown")
        
        if not url:
            print(f"[{idx}/{total}] Skipping {name} - no URL")
            fail_count += 1
            continue

        print(f"[{idx}/{total}] Embedding: {name}")
        print(f"  URL: {url}")
        
        embedding = get_embedding(url)
        
        if embedding:
            # Update MongoDB with the embedding
            col.update_one(
                {"_id": prod["_id"]}, 
                {"$set": {
                    "embedding": embedding,
                    "embedding_source": "jina-clip-v2",
                    "embedding_dim": len(embedding)
                }}
            )
            success_count += 1
            print(f"  ✓ Success (dim: {len(embedding)})\n")
        else:
            fail_count += 1
            print(f"  ✗ Failed\n")
        
        # Rate limiting - be respectful to the API
        if idx < total:
            time.sleep(1)

    print("=" * 50)
    print(f"Embedding complete!")
    print(f"Success: {success_count}")
    print(f"Failed: {fail_count}")
    print(f"Total: {total}")

if __name__ == "__main__":
    main()
