from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class User:
    """
    Domain model representing a user profile in the application.

    Attributes:
        id: Optional database identifier, None for unsaved users
        username: Unique username for the profile
        hashed_password: Optional bcrypt hash of user's password
        encrypted_api_key: Optional encrypted OpenRouter.ai API key
        default_llm_model: Optional preferred LLM model for AI operations
        app_theme: Optional preferred UI theme 
        created_at: Timestamp of profile creation
        updated_at: Timestamp of last profile update
    """

    id: Optional[int]
    username: str
    hashed_password: Optional[str] = None
    encrypted_api_key: Optional[bytes] = None
    default_llm_model: Optional[str] = None
    app_theme: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
