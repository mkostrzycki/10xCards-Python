"""Cryptographic utilities for secure data storage."""

import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from Shared.infrastructure.config import get_secret_key


class CryptoManager:
    """Manages encryption/decryption of sensitive data using Fernet."""

    def __init__(self) -> None:
        """Initialize the crypto manager with a Fernet instance."""
        self._fernet = self._setup_fernet()

    def _setup_fernet(self) -> Fernet:
        """Set up Fernet with a key derived from the application secret.

        The key is derived using PBKDF2 with a salt for additional security.
        """
        # Get the base secret from config
        secret_key = get_secret_key()

        # Use PBKDF2 to derive a key
        salt = b"10xCards"  # This is fine to be constant as we use a unique secret_key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,  # High iteration count for better security
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))

        return Fernet(key)

    def encrypt_api_key(self, api_key: str) -> bytes:
        """Encrypt an API key.

        Args:
            api_key: The plain API key to encrypt.

        Returns:
            bytes: The encrypted API key.
        """
        return self._fernet.encrypt(api_key.encode())

    def decrypt_api_key(self, encrypted_key: bytes) -> str:
        """Decrypt an encrypted API key.

        Args:
            encrypted_key: The encrypted API key to decrypt.

        Returns:
            str: The decrypted API key.

        Raises:
            cryptography.fernet.InvalidToken: If the key is invalid or corrupted.
        """
        return self._fernet.decrypt(encrypted_key).decode()


# Singleton instance for app-wide use
crypto_manager = CryptoManager()
