"""
app/config.py — Central configuration for TruthGuard AI.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_file_ignore_missing=True,
    )

    app_name: str = "TruthGuard AI"
    app_version: str = "1.0.0"
    environment: str = "development"

    # Database: SQLite for zero-setup local, PostgreSQL compatible
    database_url: str = "sqlite:///./data/truthguard.db"

    # JWT Authentication & Security
    secret_key: str = "truthguard-production-grade-super-secret-key-2026-ai"
    access_token_expire_minutes: int = 120

    # Admin Registration Secret
    admin_secret: str = "truthguard-admin-secret-key"

    # Optional AI Engine Key (Gemini API)
    # If not provided, TruthGuard uses built-in NLP & semantic RAG engine
    gemini_api_key: str | None = None


settings = Settings()
