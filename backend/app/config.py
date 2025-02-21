import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration settings loaded from environment variables"""
    
    # MongoDB settings
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "templates_db")
    
    # API settings
    API_VERSION: str = "v1"
    DEBUG: bool = os.getenv("DEBUG", False)
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Optional S3 or file storage settings
    STORAGE_BUCKET: Optional[str] = None
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")

    # OpenAI and other settings
    ALLOW_ORIGINS: str = os.getenv("ALLOW_ORIGINS", "*")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    MODEL: str = os.getenv("MODEL", "gpt-4o-mini")   
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
    EMBEDDING_DIMENSIONS: int = int(os.getenv("EMBEDDING_DIMENSIONS", 1024))
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")  
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    DOCS_DIR: str = os.getenv("DOCS_DIR", "data/docs")
    EXPORT_DIR: str = os.getenv("EXPORT_DIR", "data")
    VECTOR_SEARCH_TOP_K: int = int(os.getenv("VECTOR_SEARCH_TOP_K", 10))
    OWNER_NAME: str = os.getenv("OWNER_NAME", "")

    # Chat settings
    HISTORY_SIZE: int = 10
    MAX_TOOL_CALLS: int = 3

