"""Flashcard-related type definitions for OpenRouter API client."""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List


@dataclass(frozen=True)
class FlashcardDTO:
    """Data transfer object for a generated flashcard."""

    front: str
    back: str
    deck_id: int
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
