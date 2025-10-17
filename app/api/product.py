from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from typing import List, Optional
import tempfile
import os
import time
from app.models.product import (
    ProductResponse,
    SearchRequest,
    SearchResponse,
    SearchResult
)
from app.services.mongodb import get_products, get_product_by_id, get_all_embeddings
from app.services.jina_embeddings import get_embedding, get_embedding_from_file
from app.services.similarity import find_similar_products

router = APIRouter(prefix="/api", tags=["products"])

@router.get("/products", response_model=List[ProductResponse])
async def list_products(
    category: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0)
):
    """List all products with optional category filter"""
    products = await get_products(category=category, limit=limit, skip=skip, require_embedding=False)
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
    Search for visually similar products using image URL
    """
    start_time = time.time()
    
    # Step 1: Get embedding
    print(f"[SEARCH] Getting embedding for: {request.image_url[:50]}...")
    embed_start = time.time()
    query_embedding = await get_embedding(request.image_url)
    embed_time = time.time() - embed_start
    print(f"[SEARCH] Embedding took {embed_time:.2f}s")
    
    if not query_embedding:
        raise HTTPException(
            status_code=400,
            detail="Failed to generate embedding for the provided image URL"
        )
    
    # Step 2: Get products
    print(f"[SEARCH] Fetching products from MongoDB...")
    db_start = time.time()
    all_products = await get_all_embeddings()
    db_time = time.time() - db_start
    print(f"[SEARCH] Fetched {len(all_products)} products in {db_time:.2f}s")
    
    # Filter by category if provided
    if request.category:
        all_products = [p for p in all_products if p.get('category') == request.category]
        print(f"[SEARCH] Filtered to {len(all_products)} products in category: {request.category}")
    
    # Step 3: Find similar
    print(f"[SEARCH] Computing similarities...")
    sim_start = time.time()
    similar = find_similar_products(
        query_embedding=query_embedding,
        products=all_products,
        top_k=request.top_k,
        min_similarity=request.min_similarity
    )
    sim_time = time.time() - sim_start
    print(f"[SEARCH] Similarity computation took {sim_time:.2f}s")
    
    # Format results
    results = [
        SearchResult(
            product=ProductResponse(**product),
            similarity_score=round(score, 4)
        )
        for product, score in similar
    ]
    
    total_time = time.time() - start_time
    print(f"[SEARCH] Total search time: {total_time:.2f}s, found {len(results)} results")
    
    return SearchResponse(
        query_url=request.image_url,
        results=results,
        total_results=len(results)
    )

@router.post("/search-upload", response_model=SearchResponse)
async def search_similar_products_upload(
    file: UploadFile = File(...),
    top_k: int = Query(10, ge=1, le=50),
    min_similarity: float = Query(0.3, ge=0.0, le=1.0),
    category: Optional[str] = Query(None)
):
    """
    Search for visually similar products by uploading an image file
    """
    start_time = time.time()
    
    # Validate file type (handle None content_type)
    content_type = file.content_type or ''
    file_ext = os.path.splitext(file.filename)[1].lower() if file.filename else ''
    valid_exts = ['.jpg', '.jpeg', '.png', '.webp']
    disallowed_exts = ['.avif']
    
    # Reject AVIF explicitly (Pillow often cannot decode AVIF in server environments)
    if file_ext in disallowed_exts or content_type == 'image/avif':
        raise HTTPException(
            status_code=415,
            detail="AVIF images are not supported. Please upload PNG/JPG/JPEG/WEBP."
        )

    # Accept if content type is image/* OR if extension is valid
    if not (content_type.startswith('image/') or file_ext in valid_exts):
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Expected image file, got: {content_type or 'unknown'} with extension {file_ext}"
        )
    
    print(f"[UPLOAD] Processing file: {file.filename} (type: {content_type}, ext: {file_ext})")
    
    # Save uploaded file temporarily
    temp_file = None
    try:
        # Create temporary file
        suffix = file_ext or '.jpg'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            temp_file = tmp.name
        
        file_size_kb = len(content) / 1024
        print(f"[UPLOAD] Saved temp file: {temp_file} ({file_size_kb:.1f} KB)")
        
        # Get embedding from file
        embed_start = time.time()
        query_embedding = await get_embedding_from_file(temp_file)
        embed_time = time.time() - embed_start
        print(f"[UPLOAD] Embedding took {embed_time:.2f}s")
        
        if not query_embedding:
            raise HTTPException(
                status_code=400,
                detail="Failed to generate embedding. Please ensure the file is a valid image."
            )
        
        print(f"[UPLOAD] Got embedding with {len(query_embedding)} dimensions")
        
        # Get all products with embeddings
        print(f"[UPLOAD] Fetching products from database...")
        all_products = await get_all_embeddings()
        print(f"[UPLOAD] Found {len(all_products)} products with embeddings")
        
        # Filter by category if provided
        if category:
            all_products = [p for p in all_products if p.get('category') == category]
            print(f"[UPLOAD] Filtered to {len(all_products)} products in category: {category}")
        
        # Find similar products
        print(f"[UPLOAD] Computing similarities (min threshold: {min_similarity})...")
        similar = find_similar_products(
            query_embedding=query_embedding,
            products=all_products,
            top_k=top_k,
            min_similarity=min_similarity
        )
        
        # Format results
        results = [
            SearchResult(
                product=ProductResponse(**product),
                similarity_score=round(score, 4)
            )
            for product, score in similar
        ]
        
        total_time = time.time() - start_time
        print(f"[UPLOAD] Total time: {total_time:.2f}s, returning {len(results)} results")
        
        return SearchResponse(
            query_url=f"uploaded_file: {file.filename}",
            results=results,
            total_results=len(results)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[UPLOAD] Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        # Clean up temp file
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
                print(f"[UPLOAD] Cleaned up temp file")
            except:
                pass

@router.get("/categories")
async def get_categories():
    """Get all available product categories"""
    return {
        "categories": ["cars", "fruits", "phone", "softdrink", "tshirts"]
    }
