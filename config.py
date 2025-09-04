"""Configuration settings for the Deep Research Multi-Agent System."""

import os
from typing import Optional
try:
    from pydantic import BaseSettings
except ImportError:
    from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # API Keys
    parallel_api_key: str
    openai_api_key: str
    
    # Database
    database_url: str = "sqlite:///./deep_research.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Application
    debug: bool = True
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Parallel.ai Configuration
    search_api_base_url: str = "https://api.parallel.ai/alpha"
    chat_api_base_url: str = "https://beta.parallel.ai"
    
    # Agent Configuration
    max_search_results: int = 10
    max_chars_per_result: int = 1500
    default_processor: str = "base"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
