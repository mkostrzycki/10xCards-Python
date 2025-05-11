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
        # Make sure we're using the right HTTP endpoint pattern
        litellm.force_openai_route = True
        # Konfigurujemy domyślne nagłówki dla OpenRouter
        litellm.headers = {
            "HTTP-Referer": "https://10xcards.app",  # Opcjonalny identyfikator aplikacji
            "X-Title": "10xCards Flashcard Generator",  # Opcjonalny tytuł aplikacji
        }

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

        Makes a simple test request to verify the key using a small model.

        Args:
            api_key: The OpenRouter API key to verify.

        Returns:
            Tuple[bool, str]: A tuple containing:
                - Boolean indicating if the key is valid
                - A message providing details (error message or success)
        """
        self.logger.info("Verifying OpenRouter API key")
        self.logger.debug(f"API key to verify: {api_key[:4]}...{api_key[-4:] if len(api_key) > 8 else ''}")

        # Basic format validation for OpenRouter keys (typically start with "sk-or-")
        if not api_key.startswith("sk-or-"):
            self.logger.warning("API key validation failed: Invalid key format")
            return False, "Nieprawidłowy format klucza API (powinien zaczynać się od 'sk-or-')"

        # Włącz szczegółowe logowanie dla litellm na czas weryfikacji
        debug_was_on = False
        try:
            # Sprawdź, czy debug był już włączony
            if hasattr(litellm, "_debug"):
                debug_was_on = litellm._debug

            # Włącz debug, jeśli nie jest już włączony
            if not debug_was_on:
                self.logger.info("Enabling litellm debug mode for API key verification")
                litellm._turn_on_debug()

            # Używamy minimalnego zapytania do OpenRouter - ważne użycie poprawnego formatu modelu z prefixem "openrouter/"
            test_message = [{"role": "user", "content": "test"}]

            # Log dla diagnostyki
            self.logger.info("Sending test request to OpenRouter API")

            response = litellm.completion(
                model="openrouter/meta-llama/llama-3-8b-instruct",  # Poprawny format modelu dla OpenRouter
                messages=test_message,
                api_key=api_key,
                max_tokens=1,  # Absolutne minimum tokenów
                temperature=0.0,  # Minimalne zużycie zasobów
            )

            # Log z odpowiedzi API
            self.logger.info("OpenRouter API test request successful")
            self.logger.debug(f"Response model: {response.model}")
            self.logger.debug(f"Response choices: {response.choices}")
            self.logger.debug(f"Response usage: {response.usage}")

            return True, "API key valid"

        except litellm.exceptions.AuthenticationError as e:
            # Authentication error means invalid key
            self.logger.warning(f"API key verification failed: Invalid authentication: {str(e)}")
            return False, "Nieprawidłowy klucz API"

        except litellm.exceptions.APIConnectionError as e:
            # Connection issues
            error_msg = f"Could not connect to OpenRouter API: {str(e)}"
            self.logger.error(error_msg)
            return False, f"Błąd połączenia z API OpenRouter: {str(e)}"

        except litellm.exceptions.BadRequestError as e:
            # Bad request oznacza problem z zapytaniem - w kontekście weryfikacji klucza,
            # najczęściej wskazuje to na nieprawidłowy klucz lub autoryzację
            error_msg = f"Bad request to OpenRouter API: {str(e)}"
            self.logger.error(error_msg)

            # Sprawdź komunikat błędu dla lepszej diagnostyki
            error_str = str(e).lower()

            if "auth" in error_str or "key" in error_str or "credential" in error_str:
                return False, "Nieprawidłowy klucz API lub brak uprawnień"
            elif "rate limit" in error_str:
                return False, f"Przekroczono limit zapytań dla klucza API: {str(e)}"
            else:
                # W przypadku innych błędów, zakładamy że klucz jest niepoprawny
                return False, f"Błąd weryfikacji klucza API: {str(e)}"

        except litellm.exceptions.RateLimitError as e:
            # Rate limit error oznacza, że klucz jest prawidłowy, ale są limity
            self.logger.warning(f"API key is valid but rate limited: {str(e)}")
            return True, "API key poprawny, ale osiągnięto limit zapytań"

        except Exception as e:
            # Catch-all for other errors
            error_msg = f"Unexpected error verifying API key: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return False, f"Nieoczekiwany błąd: {str(e)}"

        finally:
            # Przywróć poprzedni stan debug
            if not debug_was_on and hasattr(litellm, "_turn_off_debug"):
                self.logger.info("Restoring original litellm debug mode")
                litellm._turn_off_debug()

    def _format_flashcard_prompt(self, raw_text: str) -> List[ChatMessage]:
        """Format the flashcard generation prompt with the input text.

        Args:
            raw_text: The text to generate flashcards from.

        Returns:
            List[ChatMessage]: The formatted messages for the chat completion.
        """
        # Komunikat systemowy definiujący zadanie
        system_message = ChatMessage(
            role="system",
            content=FLASHCARD_GENERATION_PROMPT.format(text=raw_text, schema=json.dumps(FLASHCARD_SCHEMA, indent=2)),
        )

        # Dodajemy również wiadomość od użytkownika, która jest wymagana przez modele Anthropic
        user_message = ChatMessage(role="user", content="Wygeneruj fiszki z podanego tekstu zgodnie z instrukcjami.")

        return [system_message, user_message]

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

            # Upewnij się, że model ma poprawny prefix dla OpenRouter
            if not selected_model.startswith("openrouter/"):
                selected_model = f"openrouter/{selected_model}"
                self.logger.debug(f"Added openrouter/ prefix to model: {selected_model}")

            # Prepare request parameters
            completion_params = {
                "model": selected_model,
                "messages": [msg.__dict__ for msg in messages],
                **params,
            }
            if response_format:
                completion_params["response_format"] = response_format.__dict__

            # Add debug logs for API key type
            self.logger.debug(f"API key type before request: {type(api_key)}, length: {len(api_key)}")
            if isinstance(api_key, bytes):
                self.logger.warning("API key is bytes type, converting to string")
                api_key = api_key.decode("utf-8")
                self.logger.debug(f"API key converted to string, new type: {type(api_key)}")

            # Przygotuj nagłówki uwierzytelniania zgodnie z dokumentacją OpenRouter
            headers = {
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://10xcards.app",  # Opcjonalny identyfikator aplikacji
                "X-Title": "10xCards Flashcard Generator",  # Opcjonalny tytuł aplikacji
            }

            # Dodaj logi diagnostyczne nagłówków (bez pełnego klucza API)
            masked_headers = headers.copy()
            if len(api_key) > 8:
                masked_headers["Authorization"] = f"Bearer {api_key[:4]}...{api_key[-4:]}"
            else:
                masked_headers["Authorization"] = "Bearer ********"
            self.logger.debug(f"Request headers: {masked_headers}")

            # Make API request with authentication
            self.logger.debug(f"Sending request to OpenRouter with model: {selected_model}")
            self.logger.debug(f"API base URL: {litellm.api_base}")
            self.logger.debug(f"Using OpenAI-compatible route: {litellm.force_openai_route}")
            self.logger.debug(f"Message count: {len(messages)}")

            # Ustawiamy również API key globalnie na potrzeby tego wywołania
            # (przypisanie tymczasowe, które przywrócimy po wywołaniu)
            original_api_key = litellm.api_key
            litellm.api_key = api_key

            try:
                response: ModelResponse = litellm.completion(
                    **completion_params, api_key=api_key, custom_headers=headers  # Dodajemy nagłówki bezpośrednio
                )
            finally:
                # Przywracamy oryginalny api_key
                litellm.api_key = original_api_key

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

        # Set up response format for JSON - używamy właściwej struktury zagnieżdżonej ze schematem
        response_format = ResponseFormat(type="json_schema", json_schema={"schema": FLASHCARD_SCHEMA})

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
