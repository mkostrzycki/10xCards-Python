"""AI service for flashcard generation."""

import logging
import traceback
from typing import List, Optional

from cryptography.fernet import InvalidToken

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
from Shared.infrastructure.security.crypto import crypto_manager


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

        # Decrypt the API key if it's bytes
        if isinstance(user.encrypted_api_key, bytes):
            try:
                self.logger.debug("Encrypted API key is bytes, attempting to decrypt")
                self.logger.debug(
                    f"Encrypted key type: {type(user.encrypted_api_key)}, length: {len(user.encrypted_api_key)}"
                )

                # Try to show some info about the encrypted data for diagnosis
                try:
                    if len(user.encrypted_api_key) > 0:
                        self.logger.debug(f"Encrypted key prefix (hex): {user.encrypted_api_key[:10].hex()}")
                except Exception as hex_err:
                    self.logger.debug(f"Could not display key prefix: {str(hex_err)}")

                # Attempt decryption
                api_key = crypto_manager.decrypt_api_key(user.encrypted_api_key)
                self.logger.debug(f"API key decrypted successfully, length: {len(api_key)}")

            except InvalidToken as e:
                self.logger.error(f"Invalid token during API key decryption: {str(e)}")
                self.logger.debug(f"Exception details: {traceback.format_exc()}")
                # This is likely a key mismatch - the encryption key changed
                self.logger.info("Suggesting user to reset API key in settings")
                raise AIAPIAuthError("API key could not be decoded. Please reset your API key in profile settings.")

            except ValueError as e:
                self.logger.error(f"Value error during API key decryption: {str(e)}")
                self.logger.debug(f"Exception details: {traceback.format_exc()}")
                raise AIAPIAuthError(f"API key format error: {str(e)}. Please reset your API key in profile settings.")

            except Exception as e:
                self.logger.error(f"Failed to decrypt API key: {str(e)}")
                self.logger.debug(f"Exception details: {traceback.format_exc()}")
                raise AIAPIAuthError("Unexpected error with API key. Please reset your API key in profile settings.")
        else:
            # This branch should not normally be reached
            api_key = str(user.encrypted_api_key)
            self.logger.warning(f"Unexpected API key type: {type(user.encrypted_api_key)}, converting to string")

        # Add debug logs for API key type
        self.logger.debug(f"Final API key type: {type(api_key)}")
        # Don't log the full API key in production, just a masked version
        if len(api_key) > 8:
            masked_key = f"{api_key[:4]}...{api_key[-4:]}"
        else:
            masked_key = "****"
        self.logger.debug(f"Returning API key (masked): {masked_key}")

        # Jawne castowanie typu przed zwróceniem
        return str(api_key)

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
            retry_after = error.retry_after  # Extract retry_after to local variable
            if retry_after is not None:
                return f"Przekroczono limit zapytań. Spróbuj ponownie za {str(retry_after)} sekund."
            else:
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

        # Add more diagnostic information about the API key (be careful not to log the actual key)
        self.logger.debug(
            f"API key in generate_flashcards - type: {type(api_key)}, length: {len(api_key) if api_key else 0}"
        )

        # Log request information (without sensitive data)
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
