"""Application configuration and environment loading."""

from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, ValidationError

load_dotenv()


class Settings(BaseModel):
    """Runtime configuration loaded from the local environment."""

    discord_public_key: str
    discord_bot_token: str
    discord_application_id: str
    discord_guild_id: str
    app_env: str = "development"
    log_level: str = "INFO"
    port: int = 8000

    model_config = ConfigDict(str_strip_whitespace=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load settings from environment variables and cache the result."""

    env_values = {
        "discord_public_key": _read_env("DISCORD_PUBLIC_KEY"),
        "discord_bot_token": _read_env("DISCORD_BOT_TOKEN"),
        "discord_application_id": _read_env("DISCORD_APPLICATION_ID"),
        "discord_guild_id": _read_env("DISCORD_GUILD_ID"),
        "app_env": _read_env("APP_ENV", default="development"),
        "log_level": _read_env("LOG_LEVEL", default="INFO"),
        "port": _read_env("PORT", default="8000"),
    }

    try:
        return Settings.model_validate(env_values)
    except ValidationError as exc:
        raise RuntimeError(f"Invalid application configuration: {exc}") from exc


def _read_env(name: str, default: str | None = None) -> str:
    """Read a required environment variable with a clear error message."""

    raw_value = os.getenv(name, default)
    if raw_value is None or not str(raw_value).strip():
        raise RuntimeError(f"Missing required environment variable: {name}")
    return str(raw_value).strip()
