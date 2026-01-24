# ============================================================================
# ProInvestiX Enterprise API - Configuration
# ============================================================================

from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # ==========================================================================
    # APPLICATION
    # ==========================================================================
    APP_NAME: str = "ProInvestiX API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # ==========================================================================
    # SERVER
    # ==========================================================================
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    
    # ==========================================================================
    # DATABASE
    # ==========================================================================
    DATABASE_URL: str = "sqlite+aiosqlite:///./proinvestix.db"
    
    # ==========================================================================
    # AUTHENTICATION
    # ==========================================================================
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # ==========================================================================
    # CORS
    # ==========================================================================
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    # ==========================================================================
    # ADMIN
    # ==========================================================================
    FIRST_SUPERUSER_EMAIL: str = "admin@proinvestix.ma"
    FIRST_SUPERUSER_PASSWORD: str = "admin123"
    FIRST_SUPERUSER_USERNAME: str = "admin"
    
    # ==========================================================================
    # LOGGING
    # ==========================================================================
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    
    # ==========================================================================
    # OPTIONAL: REDIS
    # ==========================================================================
    REDIS_URL: Optional[str] = None
    
    # ==========================================================================
    # OPTIONAL: EMAIL
    # ==========================================================================
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = "ProInvestiX"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export settings instance
settings = get_settings()
