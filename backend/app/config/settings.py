"""Application configuration using Pydantic Settings."""
from functools import lru_cache
from typing import List, Optional
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


INSECURE_SECRET_PLACEHOLDERS = {
    "change-this-to-a-random-32-char-secret-key-before-production",
    "your-super-secret-key-change-in-production-min-32-chars",
    "your-super-secret-key-change-in-production",
}


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
    google_redirect_uri: Optional[str] = None

    # AI provider selection
    ai_provider: str = "auto"

    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"

    # Gemmini (OpenAI-compatible endpoint)
    gemmini_api_base_url: Optional[str] = None
    gemmini_api_key: Optional[str] = None
    gemmini_model: str = "gemmini-1"
    gemmini_embedding_model: str = "gemmini-embedding-1"

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

    # Frontend URL (OAuth redirects, emails)
    frontend_url: str = "http://localhost:4200"

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def google_oauth_redirect_uri(self) -> str:
        """Redirect URI sent to Google — must match the frontend OAuth callback."""
        if self.google_redirect_uri:
            return self.google_redirect_uri
        base = self.frontend_url.rstrip("/")
        return f"{base}/auth/google/callback"

    @property
    def uses_neon_pooler(self) -> bool:
        return "neon.tech" in self.database_url and "pooler" in self.database_url

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if self.is_production:
            if self.secret_key in INSECURE_SECRET_PLACEHOLDERS or len(self.secret_key) < 32:
                raise ValueError(
                    "SECRET_KEY must be a random 32+ character string in production. "
                    "Run: python -c \"import secrets; print(secrets.token_hex(32))\""
                )
            if self.debug:
                raise ValueError("Set DEBUG=false in production")
        return self


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
