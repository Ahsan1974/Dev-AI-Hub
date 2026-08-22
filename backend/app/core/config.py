"""Application configuration loaded from the environment."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "DevAI Hub"
    app_description: str = "Discover the right AI tools for every developer task."
    version: str = "1.0.0"
    environment: Literal["development", "test", "staging", "production"] = "development"
    debug: bool = True
    # DEBUG makes the SQLite driver extremely chatty; opt in explicitly.
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    api_prefix: str = "/api"

    database_url: str = "sqlite+aiosqlite:///./devai_hub.db"
    db_echo: bool = False

    # Stored as a plain string so .env can use a comma-separated list.
    # pydantic-settings tries to JSON-decode list[str] fields and breaks on
    # "http://localhost:5173,http://127.0.0.1:5173".
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Empty key => admin write endpoints are disabled (fail closed).
    admin_api_key: str = ""

    default_page_size: int = 24
    max_page_size: int = 100

    rate_limit_enabled: bool = True
    rate_limit_requests: int = 120
    rate_limit_window_seconds: int = 60

    # Future integrations. The MVP never requires them.
    llm_provider: Literal["none", "openai", "ollama"] = "none"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    web_search_enabled: bool = False
    web_search_provider: str = "none"
    web_search_api_key: str = ""

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _normalize_cors_origins(cls, value: object) -> object:
        if isinstance(value, list):
            return ",".join(str(item).strip() for item in value if str(item).strip())
        return value

    def cors_origin_list(self) -> list[str]:
        raw = (self.cors_origins or "").strip()
        if not raw:
            return []
        if raw.startswith("["):
            import json

            parsed = json.loads(raw)
            return [str(item).strip() for item in parsed if str(item).strip()]
        return [item.strip() for item in raw.split(",") if item.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    @property
    def admin_enabled(self) -> bool:
        return bool(self.admin_api_key)

    @property
    def sync_database_url(self) -> str:
        """Driver-free URL for tooling (Alembic autogenerate, psql inspection)."""
        return (
            self.database_url.replace("+asyncpg", "+psycopg2")
            .replace("+aiosqlite", "")
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
