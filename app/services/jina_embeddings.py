 
import httpx
from config import settings
from typing import Optional

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {settings.jina_api_key}"
}

async def get_embedding(image_url: str) -> Optional[list]:
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
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                settings.jina_endpoint,
                json=payload,
                headers=headers
            )
        
        response.raise_for_status()
        data = response.json()
        
        if 'data' in data and len(data['data']) > 0:
            embedding = data['data'][0]['embedding']
            return embedding
        else:
            return None
            
    except Exception as e:
        print(f"Embedding error: {e}")
        return None
