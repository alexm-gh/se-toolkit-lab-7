"""Configuration loader for the LMS Telegram bot.

Reads secrets from .env.bot.secret file.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Bot configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env.bot.secret",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    bot_token: str = Field("", alias="BOT_TOKEN")
    lms_api_base_url: str = Field("http://localhost:42002", alias="LMS_API_BASE_URL")
    lms_api_key: str = Field("", alias="LMS_API_KEY")
    llm_api_key: str = Field("", alias="LLM_API_KEY")


settings = Settings()
