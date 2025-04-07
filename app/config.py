# app/config.py
import logging
import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    """Application configuration settings loaded from .env file."""
    model_config = SettingsConfigDict(env_file=os.path.join(BASE_DIR, '.env'), env_file_encoding='utf-8')

    PROJECT_NAME: str = "AI Text Detection API"
    LOG_LEVEL: str = "INFO"
    API_PREFIX: str = "/api/v1"

    HF_TOKEN: str | None = None
    MODEL_NAME: str = "muyiiwaa/ai_detect_modernbert"
    MODEL_MAX_LENGTH: int = 512
    DEVICE: str = "cpu" # Updated dynamically in service initialization

@lru_cache()
def get_settings() -> Settings:
    """Returns the cached application settings."""
    settings = Settings()
    if not settings.HF_TOKEN:
        # Log warning if token isn't set, as it might be required
        logging.warning("HF_TOKEN environment variable not set.")
    return settings

settings = get_settings()