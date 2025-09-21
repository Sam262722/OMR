"""
Configuration settings for the OMR Evaluation System backend.
"""

from pydantic import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # Application settings
    APP_NAME: str = "OMR Evaluation System"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REQUIRE_AUTH: bool = False  # Set to True in production
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",  # Next.js frontend
        "http://127.0.0.1:3000",
        "http://localhost:8000",  # Backend docs
    ]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # Database settings (Supabase)
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    DATABASE_URL: str = ""
    
    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [".jpg", ".jpeg", ".png", ".pdf"]
    UPLOAD_DIR: str = "uploads"
    RESULTS_DIR: str = "results"
    
    # OMR Processing settings
    MIN_CONFIDENCE_THRESHOLD: float = 0.7
    MAX_BATCH_SIZE: int = 50
    PROCESSING_TIMEOUT: int = 300  # 5 minutes
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "omr_backend.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
_settings = None


def get_settings() -> Settings:
    """Get application settings (singleton pattern)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Environment-specific configurations
def get_development_settings() -> Settings:
    """Get development environment settings."""
    settings = get_settings()
    settings.DEBUG = True
    settings.REQUIRE_AUTH = False
    settings.LOG_LEVEL = "DEBUG"
    return settings


def get_production_settings() -> Settings:
    """Get production environment settings."""
    settings = get_settings()
    settings.DEBUG = False
    settings.REQUIRE_AUTH = True
    settings.LOG_LEVEL = "INFO"
    settings.ALLOWED_ORIGINS = ["https://your-frontend-domain.com"]
    return settings