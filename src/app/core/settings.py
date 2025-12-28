from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="astral-python-template", alias="APP_NAME")
    app_env: str = Field(default="dev", alias="APP_ENV")
    app_version: str = "0.1.0"

    database_url: str = Field(
        default="postgresql+psycopg://app:app@localhost:5432/app",
        alias="DATABASE_URL",
    )

    logfire_token: str | None = Field(default=None, alias="LOGFIRE_TOKEN")

    scalar_js_url: str = Field(
        default="https://cdn.jsdelivr.net/npm/@scalar/api-reference",
        alias="SCALAR_JS_URL",
    )
    scalar_proxy_url: str = Field(default="", alias="SCALAR_PROXY_URL")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
