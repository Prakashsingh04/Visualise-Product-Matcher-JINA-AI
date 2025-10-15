import numpy as np
from typing import List, Tuple

def cosine_similarity(vec1: list, vec2: list) -> float:
    """Calculate cosine similarity between two vectors"""
    a = np.array(vec1, dtype=float)
    b = np.array(vec2, dtype=float)
    
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return float(dot_product / (norm_a * norm_b))

def find_similar_products(
    query_embedding: list,
    products: List[dict],
    top_k: int = 10,
    min_similarity: float = 0.0
) -> List[Tuple[dict, float]]:

    similarities = []
    
    for product in products:
        if 'embedding' not in product or not product['embedding']:
            continue
        
        similarity = cosine_similarity(query_embedding, product['embedding'])
        
        if similarity >= min_similarity:
            similarities.append((product, similarity))
    
    # Sort by similarity score (descending)
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    return similarities[:top_k]
