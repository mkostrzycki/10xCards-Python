"""Configuration management for the application."""

import os
from pathlib import Path
from typing import Final, List

from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Application paths
APP_ROOT: Final[Path] = Path(__file__).parent.parent.parent.parent
DATA_DIR: Final[Path] = APP_ROOT / "data"
MIGRATIONS_DIR: Final[Path] = Path(__file__).parent / "persistence" / "sqlite" / "migrations"

# Database
DATABASE_PATH: Final[Path] = DATA_DIR / "10xcards.db"


# Security
def get_secret_key() -> str:
    """Get the application secret key from environment.

    The key is used for encrypting sensitive data like API keys.
    If not set, generates a new one and warns the user.

    Returns:
        str: The secret key.

    Note:
        In production, SECRET_KEY should always be set in the environment.
        Auto-generation is only for development convenience.
    """
    key = os.getenv("SECRET_KEY")
    if not key:
        import secrets

        key = secrets.token_urlsafe(32)
        import logging

        logging.warning(
            "SECRET_KEY not found in environment. Generated new key: %s\n"
            "In production, always set SECRET_KEY in .env file!",
            key,
        )
    return key


# OpenRouter API Configuration
OPENROUTER_API_BASE: Final[str] = "https://openrouter.ai/api/v1"
DEFAULT_AI_MODEL: Final[str] = os.getenv("DEFAULT_AI_MODEL", "openrouter/openai/gpt-4o-mini")

# Available LLM models
AVAILABLE_LLM_MODELS: Final[List[str]] = [
    "openrouter/openai/gpt-4o-mini",
    "openrouter/openai/gpt-4o",
    "openrouter/anthropic/claude-3-haiku-20240307",
    "openrouter/anthropic/claude-3-5-sonnet-20240620",
]

# Available UI themes
AVAILABLE_APP_THEMES: Final[List[str]] = [
    "darkly",  # Default dark theme
    "litera",  # Light theme
    "superhero",  # Blue-based dark theme
    "solar",  # Dark green theme
    "cosmo",  # Light blue theme
    "yeti",  # Modern light theme
]
