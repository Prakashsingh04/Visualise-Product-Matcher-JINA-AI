import httpx
import base64
from config import settings
from typing import Optional
from PIL import Image
from io import BytesIO

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {settings.jina_api_key}"
}

async def get_embedding(image_url: str) -> Optional[list]:
    """Get embedding for image URL using Jina CLIP v2"""
    payload = {
        "model": "jina-clip-v2",
        "input": [{"image": image_url}]
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
            print(f"[JINA] URL embedding: {len(embedding)} dimensions")
            return embedding
        else:
            print(f"[JINA] Unexpected response format: {data}")
            return None
            
    except httpx.HTTPStatusError as e:
        print(f"[JINA] HTTP {e.response.status_code}: {e.response.text[:500]}")
        return None
    except Exception as e:
        print(f"[JINA] URL embedding error: {type(e).__name__}: {e}")
        return None

async def get_embedding_from_file(file_path: str) -> Optional[list]:
    """Get embedding from local image file"""
    try:
        # Open and process image
        img = Image.open(file_path)
        print(f"[JINA] Original image: {img.size}, mode: {img.mode}")
        
        # Convert to RGB if needed
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode in ('RGBA', 'LA'):
                background.paste(img, mask=img.split()[-1])
            else:
                background.paste(img)
            img = background
            print(f"[JINA] Converted to RGB")
        
        # Resize if too large
        max_size = 1024
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            print(f"[JINA] Resized to {new_size}")
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=90)
        image_bytes = buffer.getvalue()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        base64_size_kb = len(image_base64) / 1024
        print(f"[JINA] Base64 size: {base64_size_kb:.1f} KB")
        
        # Use same model as database embeddings
        payload = {
            "model": "jina-clip-v2",  # Explicitly set to match database
            "input": [{"image": image_base64}]
        }
        
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                settings.jina_endpoint,
                json=payload,
                headers=headers
            )
        
        print(f"[JINA] Response status: {response.status_code}")
        
        if response.status_code == 400:
            error_text = response.text
            print(f"[JINA] Bad Request Error: {error_text[:500]}")
            # Try to extract specific error
            try:
                error_json = response.json()
                print(f"[JINA] Error details: {error_json}")
            except:
                pass
            return None
        
        response.raise_for_status()
        data = response.json()
        
        if 'data' in data and len(data['data']) > 0:
            embedding = data['data'][0]['embedding']
            print(f"[JINA] File embedding: {len(embedding)} dimensions")
            return embedding
        else:
            print(f"[JINA] Unexpected response: {data}")
            return None
            
    except httpx.HTTPStatusError as e:
        print(f"[JINA] HTTP error {e.response.status_code}: {e.response.text[:500]}")
        return None
    except Exception as e:
        print(f"[JINA] File embedding error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None