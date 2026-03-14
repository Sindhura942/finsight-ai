"""Application settings and configuration"""

from typing import Optional
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables"""

    # Application
    app_name: str = "FinSight AI"
    app_version: str = "0.1.0"
    debug: bool = False

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4

    # Database
    database_url: str = "sqlite:///./finsight.db"
    database_echo: bool = False

    # OCR
    tesseract_path: Optional[str] = None
    ocr_confidence_threshold: float = 0.7

    # LLM
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    llm_temperature: float = 0.3

    # LangGraph
    langgraph_debug: bool = False

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # File upload
    max_upload_size_mb: int = 10
    allowed_extensions: list = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]

    # CORS
    cors_origins: list = ["*"]
    cors_credentials: bool = True
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]

    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached)"""
    return Settings()
