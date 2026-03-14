"""Application configuration settings"""

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings from environment variables"""

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False
    api_title: str = "FinSight AI"
    api_version: str = "0.1.0"
    api_description: str = "AI-powered financial assistant"

    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    # Database Configuration
    database_url: str = "sqlite:///./finsight.db"
    database_echo: bool = False

    # Streamlit Configuration
    streamlit_port: int = 8501

    # OCR Configuration
    tesseract_path: Optional[str] = None

    # Logging
    log_level: str = "INFO"

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


settings = Settings()
