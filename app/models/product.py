from pydantic import BaseModel, Field
from typing import Optional, List

class ProductResponse(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    category: str
    url: str
    embedding_dim: Optional[int] = None
    
    class Config:
        populate_by_name = True

class SearchRequest(BaseModel):
    image_url: str
    top_k: int = 10
    min_similarity: float = 0.0
    category: Optional[str] = None

class SearchResult(BaseModel):
    product: ProductResponse
    similarity_score: float

class SearchResponse(BaseModel):
    query_url: str
    results: List[SearchResult]
    total_results: int
