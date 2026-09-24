"""
AI Council - Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "AI Council"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Database (SQLite)
    SQLITE_DATABASE: str = "ai_council.db"

    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Groq API
    GROQ_API_KEY: str = ""
    GROQ_BASE_URL: str = "https://api.groq.com"
    GROQ_MODEL: str = "llama3-70b-8192"
    GROQ_TEMPERATURE: float = 0.7
    GROQ_MAX_TOKENS: int = 4096

    # Pinecone
    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = ""
    PINECONE_CLOUD: str = "aws"
    PINECONE_REGION: str = "us-east-1"
    PINECONE_INDEX_NAME: str = "ai-council"
    PINECONE_DIMENSION: int = 384

    # Embeddings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DEVICE: str = "cpu"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:3000"]

    # File Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "txt", "md"]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Worker
    MAX_CONCURRENT_AGENTS: int = 5
    AGENT_TIMEOUT: int = 300  # 5 minutes

    class Config:
        env_file = PROJECT_ROOT / ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
