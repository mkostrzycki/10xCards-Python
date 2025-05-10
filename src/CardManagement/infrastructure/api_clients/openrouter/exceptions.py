"""Custom exceptions for OpenRouter API client."""

from typing import Optional


class OpenRouterError(Exception):
    """Base exception for all OpenRouter-related errors."""

    pass


class AIAPIAuthError(OpenRouterError):
    """Raised when there are issues with API authentication."""

    def __init__(self, message: str = "Invalid or missing API key") -> None:
        super().__init__(message)


class AIAPIConnectionError(OpenRouterError):
    """Raised when there are network connectivity issues."""

    def __init__(self, message: str = "Failed to connect to OpenRouter API") -> None:
        super().__init__(message)


class AIAPIRequestError(OpenRouterError):
    """Raised for 4xx client errors from OpenRouter API."""

    def __init__(self, code: int, message: str) -> None:
        self.code = code
        super().__init__(f"Request error {code}: {message}")


class AIAPIServerError(OpenRouterError):
    """Raised for 5xx server errors from OpenRouter API."""

    def __init__(self, code: int, message: str = "OpenRouter API server error") -> None:
        self.code = code
        super().__init__(f"Server error {code}: {message}")


class AIRateLimitError(OpenRouterError):
    """Raised when hitting rate limits (HTTP 429)."""

    def __init__(self, retry_after: Optional[int] = None) -> None:
        self.retry_after = retry_after
        message = f"Rate limit exceeded. Retry after {retry_after} seconds" if retry_after else "Rate limit exceeded"
        super().__init__(message)


class FlashcardGenerationError(OpenRouterError):
    """Raised when there are issues with flashcard generation."""

    pass
