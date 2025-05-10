"""Type definitions for OpenRouter API client."""

from dataclasses import dataclass
from typing import Literal, Optional, Dict, Any, List


@dataclass
class ChatMessage:
    """Represents a single message in a chat completion request."""

    role: Literal["system", "user", "assistant"]
    content: str


@dataclass
class ResponseFormat:
    """Defines the expected format of the API response."""

    type: Literal["json_schema"]
    json_schema: Dict[str, Any]


@dataclass
class ChatCompletionDTO:
    """Data transfer object for chat completion response."""

    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]
    raw_response: Dict[str, Any]


@dataclass
class FlashcardDTO:
    """Data transfer object for a generated flashcard."""

    front: str
    back: str
    deck_id: int
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
