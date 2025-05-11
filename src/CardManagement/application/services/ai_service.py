"""AI service for flashcard generation."""

import logging
from typing import List, Optional, cast

from CardManagement.infrastructure.api_clients.openrouter.client import OpenRouterAPIClient
from CardManagement.infrastructure.api_clients.openrouter.exceptions import (
    AIAPIAuthError,
    AIAPIConnectionError,
    AIAPIRequestError,
    AIAPIServerError,
    AIRateLimitError,
    FlashcardGenerationError,
)
from CardManagement.infrastructure.api_clients.openrouter.types import FlashcardDTO
from Shared.application.session_service import SessionService
from Shared.infrastructure.config import DEFAULT_AI_MODEL


class AIService:
    """Application service for AI-powered features."""

    def __init__(
        self,
        api_client: OpenRouterAPIClient,
        session_service: SessionService,
        logger: logging.Logger,
    ) -> None:
        """Initialize the AI service.

        Args:
            api_client: Low-level OpenRouter API client.
            session_service: Service for accessing current user data.
            logger: Pre-configured application logger.
        """
        self.api_client = api_client
        self.session_service = session_service
        self.logger = logger

    def _get_user_api_key(self) -> str:
        """Get the API key for the current user.

        Returns:
            str: The decrypted API key.

        Raises:
            AIAPIAuthError: If no user is logged in or has no API key set.
        """
        user = self.session_service.get_current_user()
        if not user:
            raise AIAPIAuthError("No user logged in")
        if not user.encrypted_api_key:
            raise AIAPIAuthError("API key not set. Please set your OpenRouter API key in profile settings.")

        # Comment below clarifies that the value is already decrypted by the repository
        # Use cast to ensure proper type checking
        api_key = cast(str, user.encrypted_api_key)  # Already decrypted by repository

        # Add debug logs for API key type
        self.logger.debug(f"API key type in _get_user_api_key: {type(api_key)}")
        self.logger.debug(f"API key: {api_key}")
        if isinstance(api_key, bytes):
            self.logger.warning("API key is bytes, this might cause issues in litellm")

        return api_key

    def explain_error(self, error: Exception) -> str:
        """Convert an API error to a user-friendly message.

        Args:
            error: The exception to explain.

        Returns:
            str: A human-readable error message.
        """
        if isinstance(error, AIAPIAuthError):
            return "Błąd uwierzytelniania. Sprawdź swój klucz API w ustawieniach profilu."
        elif isinstance(error, AIAPIConnectionError):
            return "Nie można połączyć się z API. Sprawdź połączenie internetowe."
        elif isinstance(error, AIRateLimitError):
            if error.retry_after:
                return f"Przekroczono limit zapytań. Spróbuj ponownie za {error.retry_after} sekund."
            return "Przekroczono limit zapytań. Spróbuj ponownie później."
        elif isinstance(error, AIAPIRequestError):
            return f"Błąd zapytania: {str(error)}"
        elif isinstance(error, AIAPIServerError):
            return "Błąd serwera OpenRouter. Spróbuj ponownie później."
        elif isinstance(error, FlashcardGenerationError):
            return f"Błąd generowania fiszek: {str(error)}"
        else:
            return f"Nieoczekiwany błąd: {str(error)}"

    def generate_flashcards(
        self,
        raw_text: str,
        deck_id: int,
        *,
        model: Optional[str] = None,
    ) -> List[FlashcardDTO]:
        """Generate flashcards from the given text.

        This is a high-level method that:
        1. Gets the current user's API key
        2. Validates the input
        3. Calls the API client with appropriate parameters
        4. Returns the generated flashcards

        Args:
            raw_text: The text to generate flashcards from.
            deck_id: The ID of the deck to associate flashcards with.
            model: Optional model override. If not provided, uses the default.

        Returns:
            List[FlashcardDTO]: The generated flashcards.

        Raises:
            AIAPIAuthError: If no user is logged in or has no API key.
            AIAPIConnectionError: If there are network issues.
            AIAPIRequestError: For 4xx client errors.
            AIAPIServerError: For 5xx server errors.
            AIRateLimitError: When hitting rate limits.
            FlashcardGenerationError: If flashcard generation fails.
            ValueError: If the input text is empty or too long.
        """
        # Input validation
        if not raw_text.strip():
            raise ValueError("Tekst nie może być pusty")
        if len(raw_text) > 10000:  # Arbitrary limit to prevent token overflow
            raise ValueError("Tekst jest zbyt długi (max 10000 znaków)")

        # Get API key
        api_key = self._get_user_api_key()

        # Add more diagnostic information about the API key
        self.logger.debug(
            f"API key in generate_flashcards - type: {type(api_key)}, length: {len(api_key) if api_key else 0}"
        )
        self.logger.info(f"API key: {api_key}")

        # Log the request (without sensitive data)
        self.logger.info(
            "Generating flashcards",
            extra={
                "deck_id": deck_id,
                "text_length": len(raw_text),
                "model": model or DEFAULT_AI_MODEL,
            },
        )

        try:
            # Call the API client
            flashcards: List[FlashcardDTO] = self.api_client.generate_flashcards(
                api_key=api_key,
                raw_text=raw_text,
                deck_id=deck_id,
                model=model or DEFAULT_AI_MODEL,
                temperature=0.3,  # Lower temperature for more focused output
            )
            return flashcards

        except Exception as e:
            # Log the error
            self.logger.error(
                "Flashcard generation failed",
                extra={
                    "deck_id": deck_id,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
                exc_info=True,
            )
            raise  # Re-raise to be handled by the UI
