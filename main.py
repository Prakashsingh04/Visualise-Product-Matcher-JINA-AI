 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.product import router as product_router
from app.services.mongodb import MongoDB
from config import settings
from bson import ObjectId
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    MongoDB.connect()
    print("Connected to MongoDB Atlas")
    yield
    # Shutdown
    MongoDB.close()
    print("Closed MongoDB connection")

app = FastAPI(
    title="Visual Product Matcher API",
    description="Find visually similar products using image embeddings",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(product_router)

@app.get("/")
def read_root():
    return {
        "service": "Visual Product Matcher",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/diagnostics")
async def diagnostics():
    """Basic diagnostics for DB connectivity and collection stats"""
    info = {"status": "ok"}
    try:
        col = MongoDB.get_collection()
        # server_info forces a round-trip
        await col.database.client.server_info()
        total = await col.count_documents({})
        with_embeddings = await col.count_documents({"embedding": {"$exists": True, "$ne": None}})
        sample = await col.find_one({}, projection={"_id": 1, "category": 1})
        info.update({
            "mongo": "connected",
            "counts": {"total": int(total), "with_embeddings": int(with_embeddings)},
            "sample": {"_id": str(sample["_id"]) if sample and "_id" in sample else None, "category": sample.get("category") if sample else None}
        })
    except Exception as e:
        info.update({"mongo": "error", "error": str(e)})
    return info

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug
    )
