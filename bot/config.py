"""Configuration loader for the LMS Telegram bot.

Reads secrets from .env.bot.secret file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Bot configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env.bot.secret",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str = ""
    lms_api_base_url: str = "http://localhost:42002"
    lms_api_key: str = ""
    llm_api_key: str = ""


settings = Settings()
