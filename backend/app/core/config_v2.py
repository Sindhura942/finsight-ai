"""
Production configuration for FinSight AI.

This module provides environment-specific configurations and
production-ready settings with validation.

Examples:
    Getting configuration:
        from app.core.config import settings
        api_host = settings.api_host
"""

from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings with environment variable support.
    
    Uses pydantic for validation and BaseSettings for environment loading.
    """

    # API Configuration
    api_title: str = Field(default="FinSight AI", description="API title")
    api_version: str = Field(default="1.0.0", description="API version")
    api_description: str = Field(default="Financial intelligence platform", description="API description")
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_debug: bool = Field(default=False, description="Debug mode")

    # Environment
    environment: str = Field(default="development", description="Environment: development, staging, production")
    
    # Logging
    log_level: str = Field(default="INFO", description="Log level")
    log_format: str = Field(default="json", description="Log format: json or text")
    
    # Database
    database_url: str = Field(
        default="sqlite:///finsight.db",
        description="Database connection URL"
    )
    database_echo: bool = Field(default=False, description="Echo SQL queries")

    # CORS
    cors_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:8501",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8501",
        ],
        description="Allowed CORS origins"
    )
    cors_credentials: bool = Field(default=True, description="Allow CORS credentials")
    cors_methods: List[str] = Field(default=["*"], description="Allowed CORS methods")
    cors_headers: List[str] = Field(default=["*"], description="Allowed CORS headers")

    # Security
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Token expiration in minutes")

    # External Services
    ocr_service_timeout: int = Field(default=30, description="OCR service timeout in seconds")
    ocr_service_url: Optional[str] = Field(default=None, description="OCR service endpoint")
    ai_service_timeout: int = Field(default=30, description="AI service timeout in seconds")
    ai_service_url: Optional[str] = Field(default=None, description="AI service endpoint")

    # Cache
    cache_ttl: int = Field(default=300, description="Cache TTL in seconds")
    enable_cache: bool = Field(default=True, description="Enable caching")

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests_per_minute: int = Field(default=60, description="Requests per minute")

    # Pagination
    default_page_size: int = Field(default=20, description="Default pagination size")
    max_page_size: int = Field(default=100, description="Maximum pagination size")

    # Feature Flags
    enable_ocr: bool = Field(default=True, description="Enable OCR receipt processing")
    enable_ai_insights: bool = Field(default=True, description="Enable AI recommendations")
    enable_budget_alerts: bool = Field(default=True, description="Enable budget alerts")

    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment value."""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of: {allowed}")
        return v

    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of: {allowed}")
        return v.upper()

    @validator("api_port")
    def validate_port(cls, v):
        """Validate port number."""
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"

    @property
    def database_echo_sql(self) -> bool:
        """Should SQL queries be echoed."""
        return self.database_echo and self.is_development

    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.
    
    Returns:
        Settings instance
        
    Examples:
        >>> settings = get_settings()
        >>> settings.api_host
        "0.0.0.0"
    """
    return Settings()


# Default settings instance
settings = get_settings()
