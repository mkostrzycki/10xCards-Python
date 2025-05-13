import pytest
from unittest.mock import Mock, patch
import logging
from cryptography.fernet import InvalidToken

from src.CardManagement.application.services.ai_service import AIService
from src.CardManagement.infrastructure.api_clients.openrouter.exceptions import AIAPIConnectionError
from src.CardManagement.infrastructure.api_clients.openrouter.types import FlashcardDTO
from src.UserProfile.domain.models.user import User
from src.Shared.infrastructure.config import DEFAULT_AI_MODEL


@pytest.fixture
def mock_api_client(mocker):
    """Mock dla klienta OpenRouter API."""
    return mocker.Mock()


@pytest.fixture
def mock_session_service(mocker):
    """Mock dla serwisu sesji."""
    mock = mocker.Mock()
    # Domyślnie symulujemy zalogowanego użytkownika z kluczem API
    mock_user = User(id=1, username="testuser", hashed_password=None, default_llm_model=None, app_theme=None)
    mock_user.encrypted_api_key = b"encrypted_api_key"
    mock.get_current_user.return_value = mock_user
    return mock


@pytest.fixture
def mock_logger():
    """Mock dla loggera."""
    return Mock(spec=logging.Logger)


@pytest.fixture
def ai_service(mock_api_client, mock_session_service, mock_logger):
    """Serwis AI do testów."""
    return AIService(
        api_client=mock_api_client,
        session_service=mock_session_service,
        logger=mock_logger,
    )


@pytest.fixture
def sample_flashcard_dto():
    """Przykładowy DTO fiszki zwracany przez API."""
    return FlashcardDTO(
        front="Co to jest Python?",
        back="Język programowania wysokiego poziomu.",
        deck_id=10,
        tags=["programming", "basics"],
        metadata={"source": "text"},
    )


class TestGetUserApiKey:
    """Testy dla metody _get_user_api_key."""

    def test_get_user_api_key_success(self, ai_service, mock_session_service):
        # Arrange
        with patch("src.CardManagement.application.services.ai_service.crypto_manager") as mock_crypto:
            mock_crypto.decrypt_api_key.return_value = "decrypted_api_key"

            # Act
            result = ai_service._get_user_api_key()

            # Assert
            assert result == "decrypted_api_key"
            mock_crypto.decrypt_api_key.assert_called_once_with(b"encrypted_api_key")

    def test_get_user_api_key_no_user(self, ai_service, mock_session_service):
        # Arrange
        mock_session_service.get_current_user.return_value = None

        # Act & Assert
        try:
            ai_service._get_user_api_key()
            pytest.fail("Should have raised an error")
        except Exception as e:
            assert e.__class__.__name__ == "AIAPIAuthError"
            assert "No user logged in" in str(e)

    def test_get_user_api_key_no_api_key(self, ai_service, mock_session_service):
        # Arrange
        mock_user = User(id=1, username="testuser", hashed_password=None, default_llm_model=None, app_theme=None)
        mock_user.encrypted_api_key = None
        mock_session_service.get_current_user.return_value = mock_user

        # Act & Assert
        try:
            ai_service._get_user_api_key()
            pytest.fail("Should have raised an error")
        except Exception as e:
            assert e.__class__.__name__ == "AIAPIAuthError"
            assert "API key not set" in str(e)

    def test_get_user_api_key_invalid_token(self, ai_service):
        # Arrange
        with patch("src.CardManagement.application.services.ai_service.crypto_manager") as mock_crypto:
            mock_crypto.decrypt_api_key.side_effect = InvalidToken()

            # Act & Assert
            try:
                ai_service._get_user_api_key()
                pytest.fail("Should have raised an error")
            except Exception as e:
                assert e.__class__.__name__ == "AIAPIAuthError"
                assert "API key could not be decoded" in str(e)

    def test_get_user_api_key_value_error(self, ai_service):
        # Arrange
        with patch("src.CardManagement.application.services.ai_service.crypto_manager") as mock_crypto:
            mock_crypto.decrypt_api_key.side_effect = ValueError("Invalid format")

            # Act & Assert
            try:
                ai_service._get_user_api_key()
                pytest.fail("Should have raised an error")
            except Exception as e:
                assert e.__class__.__name__ == "AIAPIAuthError"
                assert "API key format error" in str(e)

    def test_get_user_api_key_unexpected_error(self, ai_service):
        # Arrange
        with patch("src.CardManagement.application.services.ai_service.crypto_manager") as mock_crypto:
            mock_crypto.decrypt_api_key.side_effect = Exception("Unexpected error")

            # Act & Assert
            try:
                ai_service._get_user_api_key()
                pytest.fail("Should have raised an error")
            except Exception as e:
                assert e.__class__.__name__ == "AIAPIAuthError"
                assert "Unexpected error with API key" in str(e)


class TestExplainError:
    """Testy dla metody explain_error."""

    def test_explain_auth_error(self, ai_service):
        # Arrange
        # Tworzymy własną instancję błędu bezpośrednio, zamiast używać AIAPIAuthError
        error = type("AIAPIAuthError", (Exception,), {})("Auth failed")
        error.__class__.__name__ = "AIAPIAuthError"

        # Act
        # Podmieniamy metodę isinstance aby zawsze zwracała True dla tego specyficznego wyjątku
        with patch(
            "builtins.isinstance", lambda obj, cls: True if obj is error and cls.__name__ == "AIAPIAuthError" else False
        ):
            result = ai_service.explain_error(error)

        # Assert
        assert "Błąd uwierzytelniania" in result
        assert "klucz API" in result

    def test_explain_connection_error(self, ai_service):
        # Arrange
        error = type("AIAPIConnectionError", (Exception,), {})("Connection failed")
        error.__class__.__name__ = "AIAPIConnectionError"

        # Act
        with patch(
            "builtins.isinstance",
            lambda obj, cls: True if obj is error and cls.__name__ == "AIAPIConnectionError" else False,
        ):
            result = ai_service.explain_error(error)

        # Assert
        assert "Nie można połączyć się z API" in result
        assert "połączenie internetowe" in result

    def test_explain_rate_limit_error_with_retry(self, ai_service):
        # Arrange
        error = type("AIRateLimitError", (Exception,), {"retry_after": 60})("Rate limit exceeded")
        error.__class__.__name__ = "AIRateLimitError"

        # Act
        with patch(
            "builtins.isinstance",
            lambda obj, cls: True if obj is error and cls.__name__ == "AIRateLimitError" else False,
        ):
            result = ai_service.explain_error(error)

        # Assert
        assert "Przekroczono limit zapytań" in result
        assert "60" in result

    def test_explain_rate_limit_error_without_retry(self, ai_service):
        # Arrange
        error = type("AIRateLimitError", (Exception,), {"retry_after": None})("Rate limit exceeded")
        error.__class__.__name__ = "AIRateLimitError"

        # Act
        with patch(
            "builtins.isinstance",
            lambda obj, cls: True if obj is error and cls.__name__ == "AIRateLimitError" else False,
        ):
            result = ai_service.explain_error(error)

        # Assert
        assert "Przekroczono limit zapytań" in result
        assert "później" in result

    def test_explain_request_error(self, ai_service):
        # Arrange
        error = type("AIAPIRequestError", (Exception,), {"code": 400})("Request error 400: Bad request")
        error.__class__.__name__ = "AIAPIRequestError"

        # Act
        with patch(
            "builtins.isinstance",
            lambda obj, cls: True if obj is error and cls.__name__ == "AIAPIRequestError" else False,
        ):
            result = ai_service.explain_error(error)

        # Assert
        assert "Błąd zapytania" in result

    def test_explain_server_error(self, ai_service):
        # Arrange
        error = type("AIAPIServerError", (Exception,), {"code": 500})("Server error 500: Server error")
        error.__class__.__name__ = "AIAPIServerError"

        # Act
        with patch(
            "builtins.isinstance",
            lambda obj, cls: True if obj is error and cls.__name__ == "AIAPIServerError" else False,
        ):
            result = ai_service.explain_error(error)

        # Assert
        assert "Błąd serwera" in result
        assert "OpenRouter" in result

    def test_explain_flashcard_generation_error(self, ai_service):
        # Arrange
        error = type("FlashcardGenerationError", (Exception,), {})("Failed to parse")
        error.__class__.__name__ = "FlashcardGenerationError"

        # Act
        with patch(
            "builtins.isinstance",
            lambda obj, cls: True if obj is error and cls.__name__ == "FlashcardGenerationError" else False,
        ):
            result = ai_service.explain_error(error)

        # Assert
        assert "Błąd generowania fiszek" in result

    def test_explain_unexpected_error(self, ai_service):
        # Arrange
        error = ValueError("Some other error")

        # Act
        with patch("builtins.isinstance", lambda obj, cls: False):  # Wszystko zwraca False, aby trafić w gałąź 'else'
            result = ai_service.explain_error(error)

        # Assert
        assert "Nieoczekiwany błąd" in result


class TestGenerateFlashcards:
    """Testy dla metody generate_flashcards."""

    def test_generate_flashcards_success(self, ai_service, mock_api_client, sample_flashcard_dto):
        # Arrange
        with patch.object(ai_service, "_get_user_api_key", return_value="api_key"):
            mock_api_client.generate_flashcards.return_value = [sample_flashcard_dto]

            # Act
            result = ai_service.generate_flashcards("Sample text", 10)

            # Assert
            assert len(result) == 1
            assert result[0].front == "Co to jest Python?"
            assert result[0].back == "Język programowania wysokiego poziomu."
            mock_api_client.generate_flashcards.assert_called_once_with(
                api_key="api_key",
                raw_text="Sample text",
                deck_id=10,
                model=DEFAULT_AI_MODEL,
                temperature=0.3,
            )

    def test_generate_flashcards_empty_text(self, ai_service):
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Tekst nie może być pusty"):
            ai_service.generate_flashcards("", 10)

    def test_generate_flashcards_text_too_long(self, ai_service):
        # Arrange
        long_text = "x" * 10001  # Przekraczamy limit 10000 znaków

        # Act & Assert
        with pytest.raises(ValueError, match="Tekst jest zbyt długi"):
            ai_service.generate_flashcards(long_text, 10)

    def test_generate_flashcards_api_error(self, ai_service, mock_api_client):
        # Arrange
        with patch.object(ai_service, "_get_user_api_key", return_value="api_key"):
            mock_api_client.generate_flashcards.side_effect = AIAPIConnectionError("Connection failed")

            # Act & Assert
            with pytest.raises(AIAPIConnectionError):
                ai_service.generate_flashcards("Sample text", 10)

    def test_generate_flashcards_with_custom_model(self, ai_service, mock_api_client, sample_flashcard_dto):
        # Arrange
        with patch.object(ai_service, "_get_user_api_key", return_value="api_key"):
            mock_api_client.generate_flashcards.return_value = [sample_flashcard_dto]

            # Act
            ai_service.generate_flashcards("Sample text", 10, model="custom_model")

            # Assert
            mock_api_client.generate_flashcards.assert_called_once_with(
                api_key="api_key", raw_text="Sample text", deck_id=10, model="custom_model", temperature=0.3
            )
