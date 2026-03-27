"""
Settings - MongoDB Only Configuration
All data stored in MongoDB
"""
from pydantic_settings import BaseSettings
from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env file - try multiple locations
env_paths = [
    Path(__file__).parent.parent.parent / ".env",  # From app/config/settings.py
    Path.cwd() / ".env",  # From current working directory
    Path.cwd().parent / ".env",  # From parent of current directory
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        break

class Settings(BaseSettings):
    # App
    APP_NAME: str = "BizIntel AI"
    DEBUG: bool = False
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"
    
    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # MongoDB (ONLY DATABASE)
    MONGODB_URI: str = ""
    MONGODB_DB_NAME: str = "BizIntel"
    
    @property
    def mongodb_url(self) -> str:
        """Get MongoDB URL, supporting both MONGODB_URI and MONGODB_URL env vars"""
        return self.MONGODB_URI or os.getenv("MONGODB_URL", "")
    
    # OpenRouter LLM
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "deepseek/deepseek-chat"
    
    # External APIs (Optional)
    OPENWEATHER_API_KEY: str = ""
    NEWS_API_KEY: str = ""
    
    # Data.gov.in (Optional)
    DATA_GOV_API_KEY: str = ""
    DATA_GOV_BASE_URL: str = "https://api.data.gov.in/resource"
    GDP_RESOURCE_ID: str = ""
    MSME_RESOURCE_ID: str = ""
    FUEL_PRICE_RESOURCE_ID: str = ""
    COMMODITY_PRICE_RESOURCE_ID: str = ""
    
    # Neo4j Graph Database
    NEO4J_URI: str = ""
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = ""
    
    @property
    def neo4j_username(self) -> str:
        """Get Neo4j username, supporting both NEO4J_USERNAME and NEO4J_USER env vars"""
        return self.NEO4J_USERNAME or os.getenv("NEO4J_USER", "neo4j")
    
    # Vector Database (FAISS)
    VECTOR_DB_PATH: str = "./vector_store"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    
    # RAG Settings
    RAG_CHUNK_SIZE: int = 500
    RAG_CHUNK_OVERLAP: int = 50
    RAG_TOP_K: int = 5
    RAG_SCORE_THRESHOLD: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env

settings = Settings()
