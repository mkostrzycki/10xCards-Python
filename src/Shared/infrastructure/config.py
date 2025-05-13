"""Configuration management for the application."""

import os
import secrets
import logging
import shutil
from pathlib import Path
from typing import Final, List, Tuple

from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Application paths
APP_ROOT: Final[Path] = Path(__file__).parent.parent.parent.parent
DATA_DIR: Final[Path] = Path(APP_ROOT) / "data"
MIGRATIONS_DIR: Final[Path] = Path(__file__).parent / "persistence" / "sqlite" / "migrations"

# Database
DATABASE_PATH: Final[Path] = DATA_DIR / "10xcards.db"


# Security
def get_secret_key() -> str:
    """Get the application secret key from environment.

    The key is used for encrypting sensitive data like API keys.
    If not set, checks for .env file, and if not found, creates one from .env.dist
    with a newly generated key.

    Returns:
        str: The secret key.

    Note:
        In production, SECRET_KEY should always be set in the environment.
        Auto-generation is only for development convenience.
    """
    # Try to load from environment first
    load_dotenv()
    key = os.getenv("SECRET_KEY")

    if not key:
        env_file = APP_ROOT / ".env"
        env_dist_file = APP_ROOT / ".env.dist"

        # Check if .env file exists
        if not env_file.exists():
            # Create .env from .env.dist if it exists
            if env_dist_file.exists():
                shutil.copy(env_dist_file, env_file)
                logging.info(f"Created .env file from .env.dist template at {env_file}")
            else:
                # Create empty .env file if .env.dist doesn't exist
                with open(env_file, "w") as f:
                    f.write("# Application secrets\n")
                logging.info(f"Created empty .env file at {env_file}")

        # Generate a new secret key
        key = secrets.token_urlsafe(32)

        # Add or update SECRET_KEY in .env file
        env_content = ""
        if env_file.exists():
            with open(env_file, "r") as f:
                env_content = f.read()

        # Check if SECRET_KEY already exists in the file
        if "SECRET_KEY=" in env_content:
            # Replace existing SECRET_KEY line
            lines = env_content.splitlines()
            updated_lines = []
            for line in lines:
                if line.startswith("SECRET_KEY="):
                    updated_lines.append(f"SECRET_KEY={key}")
                else:
                    updated_lines.append(line)
            env_content = "\n".join(updated_lines)
        else:
            # Append SECRET_KEY to the end of the file
            if env_content and not env_content.endswith("\n"):
                env_content += "\n"
            env_content += f"SECRET_KEY={key}\n"

        # Write the updated content back to the file
        with open(env_file, "w") as f:
            f.write(env_content)

        # Reload environment variables to pick up the new key
        load_dotenv()

        logging.warning(
            "SECRET_KEY not found in environment. Generated new key and saved to .env file: %s\n"
            "This key will be used for all future application runs.",
            key,
        )

    return key


# OpenRouter API Configuration
OPENROUTER_API_BASE: Final[str] = "https://openrouter.ai/api/v1"
DEFAULT_AI_MODEL: Final[str] = os.getenv("DEFAULT_AI_MODEL", "openrouter/openai/gpt-4o-mini")

# Available LLM models
AVAILABLE_LLM_MODELS: Final[List[str]] = [
    "openrouter/openai/gpt-4o-mini",
    "openrouter/openai/gpt-4.1",
    "openrouter/anthropic/claude-3.5-haiku",
    "openrouter/anthropic/claude-3.7-sonnet",
    "openrouter/google/gemini-2.5-flash-preview",
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

# FSRS Configuration
# Default parameters from py-fsrs documentation
FSRS_DEFAULT_PARAMETERS: Final[Tuple[float, ...]] = (
    0.40255,
    1.18385,
    3.173,
    15.69105,
    7.1949,
    0.5345,
    1.4604,
    0.0046,
    1.54575,
    0.1192,
    1.01925,
    1.9395,
    0.11,
    0.29605,
    2.2698,
    0.2315,
    2.9898,
    0.51655,
    0.6621,
)
FSRS_DEFAULT_DESIRED_RETENTION: Final[float] = 0.9
FSRS_DEFAULT_LEARNING_STEPS_MINUTES: Final[List[int]] = [1, 10]
FSRS_DEFAULT_RELEARNING_STEPS_MINUTES: Final[List[int]] = [10]
FSRS_MAXIMUM_INTERVAL: Final[int] = 36500  # Default from py-fsrs
FSRS_ENABLE_FUZZING: Final[bool] = True  # Default from py-fsrs


# Function to get all config as a dictionary
def get_config() -> dict:
    """Get all configuration as a dictionary.

    Returns:
        dict: All configuration values.
    """
    return {
        "APP_ROOT": str(APP_ROOT),
        "DATA_DIR": str(DATA_DIR),
        "DATABASE_PATH": str(DATABASE_PATH),
        "OPENROUTER_API_BASE": OPENROUTER_API_BASE,
        "DEFAULT_AI_MODEL": DEFAULT_AI_MODEL,
        "AVAILABLE_LLM_MODELS": AVAILABLE_LLM_MODELS,
        "AVAILABLE_APP_THEMES": AVAILABLE_APP_THEMES,
        "FSRS_DEFAULT_PARAMETERS": FSRS_DEFAULT_PARAMETERS,
        "FSRS_DEFAULT_DESIRED_RETENTION": FSRS_DEFAULT_DESIRED_RETENTION,
        "FSRS_DEFAULT_LEARNING_STEPS_MINUTES": FSRS_DEFAULT_LEARNING_STEPS_MINUTES,
        "FSRS_DEFAULT_RELEARNING_STEPS_MINUTES": FSRS_DEFAULT_RELEARNING_STEPS_MINUTES,
        "FSRS_MAXIMUM_INTERVAL": FSRS_MAXIMUM_INTERVAL,
        "FSRS_ENABLE_FUZZING": FSRS_ENABLE_FUZZING,
    }
