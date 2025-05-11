"""Unit tests for the CryptoManager class."""

import base64
import pytest

from cryptography.fernet import Fernet, InvalidToken

from src.Shared.infrastructure.security.crypto import CryptoManager, crypto_manager


@pytest.fixture
def patch_logging(mocker):
    """Patch all logging methods."""
    mocker.patch("src.Shared.infrastructure.security.crypto.logging.info")
    mocker.patch("src.Shared.infrastructure.security.crypto.logging.warning")
    mocker.patch("src.Shared.infrastructure.security.crypto.logging.debug")
    mocker.patch("src.Shared.infrastructure.security.crypto.logging.error")


@pytest.fixture
def patch_secret_key(mocker):
    """Patch the get_secret_key function."""
    return mocker.patch("src.Shared.infrastructure.security.crypto.get_secret_key", return_value="test_secret_key")


@pytest.fixture
def patch_basic_dependencies(patch_logging, patch_secret_key):
    """Basic setup with patched dependencies."""
    pass


@pytest.fixture
def mock_fernet(mocker):
    """Return a mocked Fernet instance."""
    return mocker.Mock(spec=Fernet)


@pytest.fixture
def crypto_manager_with_mock_fernet(mock_fernet, patch_basic_dependencies, mocker):
    """Return a CryptoManager with a mocked Fernet instance."""
    mocker.patch.object(CryptoManager, "_setup_fernet", return_value=mock_fernet)
    return CryptoManager()


class TestCryptoManager:
    """Tests for the CryptoManager class."""

    def test_init_calls_setup_fernet(self, patch_basic_dependencies, mocker):
        """Test that __init__ calls _setup_fernet."""
        mock_setup = mocker.patch.object(CryptoManager, "_setup_fernet")
        mock_setup.return_value = mocker.Mock()

        manager = CryptoManager()

        mock_setup.assert_called_once()
        assert manager._fernet == mock_setup.return_value

    def test_setup_fernet_creates_fernet_instance(self, patch_basic_dependencies, mocker):
        """Test that _setup_fernet creates a Fernet instance with the correct key."""
        mock_fernet = mocker.patch("src.Shared.infrastructure.security.crypto.Fernet")
        mock_pbkdf2 = mocker.patch("src.Shared.infrastructure.security.crypto.PBKDF2HMAC")

        # Mock the key derivation
        mock_pbkdf2_instance = mocker.Mock()
        mock_pbkdf2.return_value = mock_pbkdf2_instance
        mock_pbkdf2_instance.derive.return_value = b"derived_key"

        # Create the manager
        CryptoManager()

        # Verify PBKDF2HMAC was called with correct parameters
        mock_pbkdf2.assert_called_once()
        mock_pbkdf2_instance.derive.assert_called_once_with(b"test_secret_key")

        # Verify Fernet was created with the correct key
        expected_key = base64.urlsafe_b64encode(b"derived_key")
        mock_fernet.assert_called_once_with(expected_key)

    def test_encrypt_api_key_successful(self, crypto_manager_with_mock_fernet, mock_fernet):
        """Test successful encryption of an API key."""
        # Setup mock behavior
        mock_fernet.encrypt.return_value = b"encrypted_data"

        # Test encryption with valid input
        result = crypto_manager_with_mock_fernet.encrypt_api_key("test_api_key")

        # Verify correct calls and output
        mock_fernet.encrypt.assert_called_once()
        assert result == b"encrypted_data"

    def test_encrypt_api_key_with_exception(self, crypto_manager_with_mock_fernet, mock_fernet):
        """Test exception handling during encryption."""
        # Setup mock to raise exception
        mock_fernet.encrypt.side_effect = Exception("Test error")

        # Call should propagate the exception
        with pytest.raises(Exception) as excinfo:
            crypto_manager_with_mock_fernet.encrypt_api_key("test_api_key")

        # Verify exception message
        assert "Test error" in str(excinfo.value)

    def test_decrypt_api_key_successful(self, crypto_manager_with_mock_fernet, mock_fernet):
        """Test successful decryption of an API key."""
        # Setup mock behavior
        mock_fernet.decrypt.return_value = b"decrypted_data"

        # Test decryption with valid input
        result = crypto_manager_with_mock_fernet.decrypt_api_key(b"encrypted_data")

        # Verify correct calls and output
        mock_fernet.decrypt.assert_called_once()
        assert result == "decrypted_data"

    def test_decrypt_api_key_with_invalid_token(self, crypto_manager_with_mock_fernet, mock_fernet):
        """Test decryption with an invalid token."""
        # Setup mock to raise InvalidToken
        mock_fernet.decrypt.side_effect = InvalidToken()

        # Call should raise exception
        with pytest.raises(Exception):
            crypto_manager_with_mock_fernet.decrypt_api_key(b"invalid_data")

    def test_singleton_instance(self):
        """Test that crypto_manager is a singleton instance."""
        assert isinstance(crypto_manager, CryptoManager)

    def test_encrypt_and_decrypt_cycle(self, crypto_manager_with_mock_fernet, mock_fernet):
        """Test that a string encrypted and then decrypted returns the original value."""
        # Original value
        original = "my_secret_api_key"

        # Setup mocks for encryption and decryption
        encrypted_data = b"encrypted_data"
        mock_fernet.encrypt.return_value = encrypted_data
        mock_fernet.decrypt.return_value = original.encode()

        # First encrypt
        encrypted = crypto_manager_with_mock_fernet.encrypt_api_key(original)

        # Then decrypt
        decrypted = crypto_manager_with_mock_fernet.decrypt_api_key(encrypted)

        # Verify calls
        mock_fernet.encrypt.assert_called_once_with(original.encode())
        mock_fernet.decrypt.assert_called_once_with(encrypted_data)

        # Verify result
        assert decrypted == original
