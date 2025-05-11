"""Cryptographic utilities for secure data storage."""

import base64
import logging
import traceback

from cryptography.fernet import Fernet, InvalidToken
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
        logging.info(f"Encrypting API key of length {len(api_key)}")
        try:
            # Ensure input is str and convert to bytes
            if not isinstance(api_key, str):
                logging.warning(f"Input API key is not a string, type: {type(api_key)}, converting")
                api_key = str(api_key)

            # Encrypt using Fernet
            input_bytes = api_key.encode("utf-8")
            logging.debug(f"Input converted to bytes, length: {len(input_bytes)}")

            encrypted = self._fernet.encrypt(input_bytes)

            # Ensure output is bytes
            if not isinstance(encrypted, bytes):
                logging.error(f"Encryption produced non-bytes output: {type(encrypted)}")
                # Try to convert if not bytes
                encrypted = bytes(encrypted)

            logging.info(f"API key encrypted successfully, result length: {len(encrypted)}")
            logging.debug(f"Encrypted key start (hex): {encrypted[:10].hex()}...")
            return encrypted
        except Exception as e:
            logging.error(f"Error encrypting API key: {str(e)}")
            logging.error(f"Exception details: {traceback.format_exc()}")
            raise

    def decrypt_api_key(self, encrypted_key: bytes) -> str:
        """Decrypt an encrypted API key.

        Args:
            encrypted_key: The encrypted API key to decrypt.

        Returns:
            str: The decrypted API key.

        Raises:
            InvalidToken: If the key is invalid or corrupted.
            ValueError: If input type is invalid.
        """
        logging.info(f"Decrypting API key of length {len(encrypted_key)}")
        logging.debug(f"Encrypted key type: {type(encrypted_key)}")

        # Debug the encrypted key in hex format
        if isinstance(encrypted_key, bytes) and len(encrypted_key) > 0:
            logging.debug(f"Encrypted key prefix (hex): {encrypted_key[:10].hex()}")

        # Ensure input is bytes
        if not isinstance(encrypted_key, bytes):
            error_msg = f"Input encrypted key is not bytes, type: {type(encrypted_key)}"
            logging.warning(error_msg)
            try:
                if isinstance(encrypted_key, str):
                    # If it's a string, try to decode from hex or convert directly to bytes
                    try:
                        encrypted_key = bytes.fromhex(encrypted_key)
                        logging.info("Converted hex string to bytes")
                    except ValueError:
                        encrypted_key = encrypted_key.encode("utf-8")
                        logging.info("Converted string to bytes using UTF-8")
                else:
                    encrypted_key = bytes(encrypted_key)
            except Exception as e:
                detailed_error = f"Failed to convert encrypted key to bytes: {str(e)}"
                logging.error(detailed_error)
                logging.error(f"Exception details: {traceback.format_exc()}")
                raise ValueError(detailed_error)

        try:
            # Perform the decryption
            decrypted = self._fernet.decrypt(encrypted_key).decode("utf-8")
            logging.info(f"API key decrypted successfully, result length: {len(decrypted)}")
            return decrypted
        except InvalidToken as e:
            # Specific error for invalid tokens
            detailed_error = (
                f"Invalid token error: The key appears to be corrupted or was encrypted with a different key: {str(e)}"
            )
            logging.error(detailed_error)
            logging.error(f"Exception details: {traceback.format_exc()}")
            raise InvalidToken(detailed_error)
        except UnicodeDecodeError as e:
            # Handle encoding errors separately
            detailed_error = f"Unicode decode error: The decrypted data is not valid UTF-8: {str(e)}"
            logging.error(detailed_error)
            logging.error(f"Exception details: {traceback.format_exc()}")
            raise ValueError(detailed_error)
        except Exception as e:
            # Generic catch-all for other errors
            detailed_error = f"Error decrypting API key: {str(e)}"
            logging.error(detailed_error)
            logging.error(f"Exception details: {traceback.format_exc()}")
            raise ValueError(detailed_error)


# Singleton instance for app-wide use
crypto_manager = CryptoManager()
