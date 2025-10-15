import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # MongoDB
    mongo_uri: str
    mongo_db: str = "visual_product_matcher"
    mongo_col: str = "products"
    
    # Jina API
    jina_api_key: str = ""
    jina_endpoint: str = "https://api.jina.ai/v1/embeddings"
    
    # App settings
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    env: str = "development"
    debug: bool = True
    
    # Optional fields that may exist in .env
    log_level: Optional[str] = "info"
    cloudinary_url: Optional[str] = None
    image_base_url: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # This allows extra fields in .env without errors

settings = Settings()
