from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.product import (
    ProductResponse,
    SearchRequest,
    SearchResponse,
    SearchResult
)
from app.services.mongodb import get_products, get_product_by_id, get_all_embeddings
from app.services.jina_embeddings import get_embedding
from app.services.similarity import find_similar_products

router = APIRouter(prefix="/api", tags=["products"])

@router.get("/products", response_model=List[ProductResponse])
async def list_products(
    category: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0)
):
    """List all products with optional category filter"""
    products = await get_products(category=category, limit=limit, skip=skip)
    return products

@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    """Get a single product by ID"""
    product = await get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/search", response_model=SearchResponse)
async def search_similar_products(request: SearchRequest):
    """
    Search for visually similar products
    Accepts image URL and returns top similar products
    """
    # Get embedding for query image
    query_embedding = await get_embedding(request.image_url)
    
    if not query_embedding:
        raise HTTPException(
            status_code=400,
            detail="Failed to generate embedding for the provided image URL"
        )
    
    # Get all products with embeddings
    all_products = await get_all_embeddings()
    
    # Filter by category if provided
    if request.category:
        all_products = [p for p in all_products if p.get('category') == request.category]
    
    # Find similar products
    similar = find_similar_products(
        query_embedding=query_embedding,
        products=all_products,
        top_k=request.top_k,
        min_similarity=request.min_similarity
    )
    
    # Format results
    results = [
        SearchResult(
            product=ProductResponse(**product),
            similarity_score=round(score, 4)
        )
        for product, score in similar
    ]
    
    return SearchResponse(
        query_url=request.image_url,
        results=results,
        total_results=len(results)
    )

@router.get("/categories")
async def get_categories():
    """Get all available product categories"""
    return {
        "categories": ["cars", "fruits", "phone", "softdrink", "tshirts"]
    }
