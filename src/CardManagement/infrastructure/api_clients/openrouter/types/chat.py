"""Chat-related type definitions for OpenRouter API client."""

from dataclasses import dataclass
from typing import Literal, Dict, Any, List


@dataclass(frozen=True)
class ChatMessage:
    """Represents a single message in a chat completion request."""

    role: Literal["system", "user", "assistant"]
    content: str


@dataclass(frozen=True)
class ResponseFormat:
    """Defines the expected format of the API response."""

    type: Literal["json_schema"]
    json_schema: Dict[str, Any]


@dataclass(frozen=True)
class ChatCompletionDTO:
    """Data transfer object for chat completion response."""

    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]
    raw_response: Dict[str, Any]
