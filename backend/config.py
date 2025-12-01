import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # AI/LLM
    openai_api_key: str = ""
    gemini_api_key: str = ""
    use_gemini: str = "true"
    
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/portfolio_v2"
    
    # Authentication
    secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Email
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    sender_email: str = ""
    sender_name: str = "Portfolio Generator"
    
    # Cloudinary
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # Deployment Platforms
    vercel_token: str = ""
    netlify_token: str = ""
    
    # Application
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"
    
    # Rate Limiting
    rate_limit_generation: str = "10/hour"
    rate_limit_upload: str = "20/hour"
    rate_limit_deploy: str = "5/hour"
    
    # Caching
    cache_ttl_portfolios: int = 3600
    cache_ttl_sessions: int = 86400
    
    # File Upload
    max_upload_size_mb: int = 10
    allowed_upload_types: str = "pdf,docx,doc,txt"
    
    # Analytics
    enable_analytics: bool = True
    analytics_retention_days: int = 90
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Allow extra fields from .env

settings = Settings()

