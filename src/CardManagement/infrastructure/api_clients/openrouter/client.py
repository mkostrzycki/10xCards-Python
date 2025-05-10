"""OpenRouter API client implementation using litellm."""

import json
import logging
from typing import List, Optional, Any, NoReturn, Tuple, cast

import litellm
from litellm import ModelResponse
from tenacity import retry, stop_after_attempt, wait_exponential

from .exceptions import (
    AIAPIAuthError,
    AIAPIConnectionError,
    AIAPIRequestError,
    AIAPIServerError,
    AIRateLimitError,
    FlashcardGenerationError,
    OpenRouterError,
)
from .prompts import FLASHCARD_GENERATION_PROMPT, FLASHCARD_SCHEMA
from .types import ChatMessage, ResponseFormat, ChatCompletionDTO, FlashcardDTO


class OpenRouterAPIClient:
    """Client for interacting with OpenRouter API via litellm."""

    def __init__(
        self,
        logger: logging.Logger,
        default_model: Optional[str] = None,
    ) -> None:
        """Initialize the OpenRouter API client.

        Args:
            logger: Pre-configured application logger.
            default_model: Optional default model to use for completions.
                         If not provided, must be specified in each request.
        """
        self.logger = logger
        self.default_model = default_model
        self._configure_litellm()

    def _configure_litellm(self) -> None:
        """Configure litellm settings."""
        # Ensure HTTPS is enforced
        litellm.api_base = "https://openrouter.ai/api/v1"

    def _handle_litellm_error(self, error: Exception) -> NoReturn:
        """Handle litellm exceptions and convert them to our custom exceptions.

        Args:
            error: The original litellm exception.

        Raises:
            OpenRouterError: An appropriate custom exception based on the error type.
        """
        if isinstance(error, litellm.exceptions.AuthenticationError):
            raise AIAPIAuthError(str(error))
        elif isinstance(error, litellm.exceptions.RateLimitError):
            retry_after = getattr(error, "retry_after", None)
            raise AIRateLimitError(retry_after)
        elif isinstance(error, litellm.exceptions.BadRequestError):
            raise AIAPIRequestError(400, str(error))
        elif isinstance(error, litellm.exceptions.ServiceUnavailableError):
            raise AIAPIServerError(503, str(error))
        elif isinstance(error, (litellm.exceptions.Timeout, litellm.exceptions.APIConnectionError)):
            raise AIAPIConnectionError(str(error))
        else:
            self.logger.error(f"Unexpected error in OpenRouter API client: {error}", exc_info=True)
            raise

    def verify_key(self, api_key: str) -> Tuple[bool, str]:
        """Verify if the API key is valid by making a lightweight API call.

        Makes a simple GET request to the /models endpoint to validate the key
        without consuming significant quota.

        Args:
            api_key: The OpenRouter API key to verify.

        Returns:
            Tuple[bool, str]: A tuple containing:
                - Boolean indicating if the key is valid
                - A message providing details (error message or success)
        """
        self.logger.info("Verifying OpenRouter API key")

        try:
            # Make a lightweight call to get available models
            # In litellm 1.66.0, use the completion method with a lightweight model check
            # instead of get_models which doesn't exist
            litellm.completion(
                model="openrouter/mistral-7b-instruct",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=1,  # Minimal tokens to reduce cost
                api_key=api_key,
            )

            # If we get here, the key is valid
            self.logger.info("API key verification successful")
            return True, "API key valid"

        except litellm.exceptions.AuthenticationError as e:
            self.logger.warning(f"API key verification failed: {str(e)}")
            return False, "Invalid API key"

        except (litellm.exceptions.Timeout, litellm.exceptions.APIConnectionError) as e:
            error_msg = f"Could not verify API key: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"Unexpected error verifying API key: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return False, error_msg

    def _format_flashcard_prompt(self, raw_text: str) -> List[ChatMessage]:
        """Format the flashcard generation prompt with the input text.

        Args:
            raw_text: The text to generate flashcards from.

        Returns:
            List[ChatMessage]: The formatted messages for the chat completion.
        """
        return [
            ChatMessage(
                role="system",
                content=FLASHCARD_GENERATION_PROMPT.format(
                    text=raw_text, schema=json.dumps(FLASHCARD_SCHEMA, indent=2)
                ),
            )
        ]

    def _parse_flashcard_response(self, response: ChatCompletionDTO, deck_id: int) -> List[FlashcardDTO]:
        """Parse the API response into flashcard DTOs.

        Args:
            response: The raw API response.
            deck_id: The ID of the deck to associate flashcards with.

        Returns:
            List[FlashcardDTO]: The parsed flashcards.

        Raises:
            FlashcardGenerationError: If the response is invalid or can't be parsed.
        """
        try:
            # Get the content from the first choice
            if not response.choices or "content" not in response.choices[0]:
                raise FlashcardGenerationError("Invalid API response format")

            # Parse the JSON content
            content = response.choices[0]["content"]
            data = json.loads(content)

            # Validate against our schema
            if "flashcards" not in data:
                raise FlashcardGenerationError("Response missing 'flashcards' array")

            # Convert to DTOs
            flashcards = []
            for card in data["flashcards"]:
                if "front" not in card or "back" not in card:
                    continue  # Skip invalid cards
                flashcards.append(
                    FlashcardDTO(
                        front=card["front"],
                        back=card["back"],
                        deck_id=deck_id,
                        tags=card.get("tags"),
                        metadata=card.get("metadata"),
                    )
                )

            if not flashcards:
                raise FlashcardGenerationError("No valid flashcards generated")

            return flashcards

        except json.JSONDecodeError as e:
            raise FlashcardGenerationError(f"Invalid JSON in response: {str(e)}")
        except Exception as e:
            raise FlashcardGenerationError(f"Error parsing flashcards: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry_error_callback=lambda retry_state: retry_state.outcome.result() if retry_state.outcome else None,
    )
    def chat_completion(
        self,
        api_key: str,
        messages: List[ChatMessage],
        *,
        model: Optional[str] = None,
        response_format: Optional[ResponseFormat] = None,
        **params: Any,
    ) -> ChatCompletionDTO:
        """Send a chat completion request to OpenRouter API.

        Args:
            api_key: OpenRouter API key for authentication.
            messages: List of chat messages for the completion.
            model: Model identifier to use for completion. If not provided,
                  uses the default_model specified in constructor.
            response_format: Optional response format specification.
            **params: Additional parameters to pass to the API.

        Returns:
            ChatCompletionDTO containing the API response.

        Raises:
            AIAPIAuthError: If the API key is invalid or missing.
            AIAPIConnectionError: If there are network connectivity issues.
            AIAPIRequestError: For 4xx client errors.
            AIAPIServerError: For 5xx server errors.
            AIRateLimitError: When hitting rate limits.
            ValueError: If no model is specified (neither in request nor default).
        """
        # Validate model selection
        selected_model = model or self.default_model
        if not selected_model:
            raise ValueError("No model specified. Provide either in the request or set a default_model.")

        try:
            # Log request metadata (not content for privacy)
            self.logger.info(
                "Sending chat completion request",
                extra={
                    "model": selected_model,
                    "message_count": len(messages),
                    "has_response_format": response_format is not None,
                },
            )

            # Prepare request parameters
            completion_params = {
                "model": selected_model,
                "messages": [msg.__dict__ for msg in messages],
                **params,
            }
            if response_format:
                completion_params["response_format"] = response_format.__dict__

            # Make API request with authentication
            response: ModelResponse = litellm.completion(
                **completion_params,
                api_key=api_key,
            )

            # Extract and convert the necessary fields from ModelResponse
            choices = (
                [
                    {
                        "content": (
                            choice.message.content
                            if hasattr(choice, "message") and hasattr(choice.message, "content")
                            else None
                        ),
                        "role": (
                            choice.message.role
                            if hasattr(choice, "message") and hasattr(choice.message, "role")
                            else "assistant"
                        ),
                        "index": choice.index if hasattr(choice, "index") else 0,
                        # Add any other fields that might be needed
                    }
                    for choice in response.choices
                ]
                if hasattr(response, "choices")
                else []
            )

            usage = (
                {
                    "prompt_tokens": (
                        response.usage.prompt_tokens
                        if hasattr(response, "usage") and hasattr(response.usage, "prompt_tokens")
                        else 0
                    ),
                    "completion_tokens": (
                        response.usage.completion_tokens
                        if hasattr(response, "usage") and hasattr(response.usage, "completion_tokens")
                        else 0
                    ),
                    "total_tokens": (
                        response.usage.total_tokens
                        if hasattr(response, "usage") and hasattr(response.usage, "total_tokens")
                        else 0
                    ),
                }
                if hasattr(response, "usage")
                else {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            )

            # Convert to DTO
            return ChatCompletionDTO(
                model=cast(str, response.model),  # Cast to ensure str type
                choices=choices,
                usage=usage,
                raw_response=response.__dict__,
            )

        except Exception as e:
            self._handle_litellm_error(e)

    def generate_flashcards(
        self,
        api_key: str,
        raw_text: str,
        deck_id: int,
        *,
        model: Optional[str] = None,
        temperature: float = 0.3,
    ) -> List[FlashcardDTO]:
        """Generate flashcards from the given text.

        Args:
            api_key: OpenRouter API key for authentication.
            raw_text: The text to generate flashcards from.
            deck_id: The ID of the deck to associate flashcards with.
            model: Optional model override for this specific generation.
            temperature: Controls randomness in the generation (0.0 to 1.0).

        Returns:
            List[FlashcardDTO]: The generated flashcards.

        Raises:
            FlashcardGenerationError: If flashcard generation fails.
            AIAPIAuthError: If the API key is invalid.
            AIAPIConnectionError: If there are network issues.
            AIAPIRequestError: For 4xx client errors.
            AIAPIServerError: For 5xx server errors.
            AIRateLimitError: When hitting rate limits.
        """
        # Format the prompt
        messages = self._format_flashcard_prompt(raw_text)

        # Set up response format for JSON
        response_format = ResponseFormat(type="json_schema", json_schema=FLASHCARD_SCHEMA)

        try:
            # Make the API request
            response = self.chat_completion(
                api_key=api_key,
                messages=messages,
                model=model,
                response_format=response_format,
                temperature=temperature,
            )

            # Parse and return the flashcards
            return self._parse_flashcard_response(response, deck_id)

        except OpenRouterError:
            # Re-raise API errors as is
            raise
        except Exception as e:
            # Wrap any other errors
            raise FlashcardGenerationError(f"Unexpected error in flashcard generation: {str(e)}")
