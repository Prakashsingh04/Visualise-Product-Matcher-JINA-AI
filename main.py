 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.product import router as product_router
from app.services.mongodb import MongoDB
from config import settings

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug
    )
