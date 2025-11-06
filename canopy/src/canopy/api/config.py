"""
API Configuration - Application settings and configuration.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings and configuration."""

    # API Settings
    app_name: str = "Canopy Trading Language API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api"

    # CORS Settings
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]

    # API Keys (basic auth)
    api_keys: List[str] = ["dev-api-key-12345"]  # In production, use env vars
    enable_auth: bool = False  # Disabled for MVP

    # Rate Limiting
    rate_limit_enabled: bool = False  # Disabled for MVP
    rate_limit_per_minute: int = 60

    # Job Queue Settings
    max_concurrent_jobs: int = 5
    job_timeout_seconds: int = 300  # 5 minutes

    # Data Provider Settings
    default_data_provider: str = "yahoo"

    # Backtest Settings
    default_initial_capital: float = 10000.0
    default_commission: float = 0.001  # 0.1%
    default_slippage: float = 0.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
