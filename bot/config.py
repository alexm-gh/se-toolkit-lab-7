"""Configuration loader for the LMS Telegram bot.

Reads secrets from .env.bot.secret file in the project root.
"""

import logging
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# Get the project root directory (parent of bot/)
PROJECT_ROOT = Path(__file__).parent.parent


class Settings(BaseSettings):
    """Bot configuration settings."""

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env.bot.secret"),
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    bot_token: str = Field("", alias="BOT_TOKEN")
    lms_api_base_url: str = Field("http://host.docker.internal:42002", alias="LMS_API_BASE_URL")
    lms_api_key: str = Field("", alias="LMS_API_KEY")
    llm_api_base_url: str = Field("http://host.docker.internal:42005/v1", alias="LLM_API_BASE_URL")
    llm_api_key: str = Field("", alias="LLM_API_KEY")
    llm_api_model: str = Field("coder-model", alias="LLM_API_MODEL")


settings = Settings()

# Log loaded settings for debugging (without secrets)
logger.debug(f"Settings loaded:")
logger.debug(f"  LMS_API_BASE_URL: {settings.lms_api_base_url}")
logger.debug(f"  LLM_API_BASE_URL: {settings.llm_api_base_url}")
logger.debug(f"  LLM_API_MODEL: {settings.llm_api_model}")
logger.debug(f"  BOT_TOKEN set: {bool(settings.bot_token)}")
logger.debug(f"  LMS_API_KEY set: {bool(settings.lms_api_key)}")
logger.debug(f"  LLM_API_KEY set: {bool(settings.llm_api_key)}")
