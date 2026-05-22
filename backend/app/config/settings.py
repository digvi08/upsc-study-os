"""Application configuration using Pydantic Settings."""
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "AI UPSC Study OS"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Google OAuth
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_redirect_uri: str = "http://localhost:8000/api/v1/auth/google/callback"

    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Cloudinary
    cloudinary_cloud_name: Optional[str] = None
    cloudinary_api_key: Optional[str] = None
    cloudinary_api_secret: Optional[str] = None

    # AWS S3
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_bucket_name: Optional[str] = None
    aws_region: str = "ap-south-1"

    # CORS
    allowed_origins: str = "http://localhost:4200"

    # Rate Limiting
    rate_limit_per_minute: int = 60

    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None

    # Frontend URL (used in emails / OAuth redirects)
    frontend_url: str = "http://localhost:4200"

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
