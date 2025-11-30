import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str = ""
    gemini_api_key: str = ""
    use_gemini: str = "true"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/portfolio_v2"
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Allow extra fields from .env

settings = Settings()
