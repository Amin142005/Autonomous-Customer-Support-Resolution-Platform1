"""Application settings loaded from environment variables.

Pydantic Settings automatically reads `.env` files.  All attributes are
typed and validated on import; missing values fall back to the documented
defaults.  Override anything via environment variables or a `.env` file
placed next to `backend/app/main.py`.
"""

from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All configurable knobs for the CloudDesk support platform."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # -- Application ---------------------------------------------------------
    APP_NAME: str = "CloudDesk Support"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    # Comma-separated list of origins for CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # -- Database -----------------------------------------------------------
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/support.db"
    # Checkpoint database for LangGraph persistence (can be same as main)
    CHECKPOINT_DB_URL: str = "sqlite+aiosqlite:///./data/checkpoints.db"

    # -- Server -------------------------------------------------------------
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    # -- LLM / AI provider --------------------------------------------------
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    # Ollama (local fallback)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1"
    # OpenRouter (multi-provider fallback)
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "google/gemini-2.5-pro-exp-03-25:free"
    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_DEPLOYMENT_NAME: str = ""

    # -- Vector embeddings --------------------------------------------------
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS: int = 1536

    # -- Redis (memory, rate-limiting, cache) -------------------------------
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 10

    # -- Authentication -----------------------------------------------------
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # -- API ---------------------------------------------------------------
    API_PREFIX: str = "/api/v1"
    # Rate-limit: max requests per minute per IP (0 = disabled)
    RATE_LIMIT_PER_MINUTE: int = 60

    # -- Logging -----------------------------------------------------------
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "json"
    LOG_DIR: str = "logs"
    LOG_MAX_BYTES: int = 10 * 1024 * 1024  # 10 MB
    LOG_BACKUP_COUNT: int = 3

    # -- LangGraph ---------------------------------------------------------
    LANGGRAPH_CHECKPOINTING_ENABLED: bool = True
    # Max steps in a single workflow run before force-terminating
    WORKFLOW_MAX_STEPS: int = 50

    # -- Integrations (mock) -----------------------------------------------
    MOCK_SERVICES_ENABLED: bool = True

    # -- Knowledge base ----------------------------------------------------
    KNOWLEDGE_DIR: str = "sample_data/knowledge_base"
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50

    @property
    def cors_origins_list(self) -> List[str]:
        """Return CORS origins as a list of strings."""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings singleton.

    Pydantic's `SettingsConfigDict` already caches, but the lru_cache wrapper
    makes the intent explicit for FastAPI dependency injection.
    """
    return Settings()
