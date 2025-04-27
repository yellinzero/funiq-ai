import base64
import os
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from loguru import logger
from sqlalchemy import JSON, String, TypeDecorator

from configs import funiq_ai_config
from utils.common.json import json_dumps, json_loads


class EncryptedType(TypeDecorator):
    """
    SQLAlchemy type that provides transparent data encryption and decryption.
    Uses Fernet symmetric encryption algorithm.
    """

    impl = String  # Use String type to store encrypted data

    cache_ok = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fernet = self._get_or_create_fernet()

    def _get_or_create_fernet(self):
        """Get or create Fernet instance using the database config"""
        try:
            key = funiq_ai_config.DB_ENCRYPTION_KEY
            if isinstance(key, str):
                key = key.encode()
            return Fernet(key)
        except Exception as e:
            logger.error(f"Failed to create Fernet instance: {e!s}")
            raise ValueError(f"Invalid encryption key: {e!s}") from e

    def process_bind_param(self, value: Any, dialect) -> str | None:
        """Encrypt value and convert to database format"""
        if value is None:
            return None

        try:
            # Convert to JSON string
            value_json = json_dumps(value)
            # Encrypt
            encrypted_data = self._fernet.encrypt(value_json.encode("utf-8"))
            # Return Base64 encoded string
            return encrypted_data.decode("utf-8")
        except Exception as e:
            logger.error(f"Failed to encrypt data: {e!s}")
            raise

    def process_result_value(self, value: str | None, dialect) -> Any:
        """Decrypt value from database"""
        if value is None:
            return None

        try:
            # Decrypt
            decrypted_data = self._fernet.decrypt(value.encode("utf-8"))
            # Parse JSON
            return json_loads(decrypted_data.decode("utf-8"))
        except InvalidToken:
            logger.error("Decryption failed: Invalid token or key mismatch")
            # Return None instead of raising exception to prevent application crash
            return None
        except Exception as e:
            logger.error(f"Failed to decrypt data: {e!s}")
            return None


class EncryptedJSON(TypeDecorator):
    """
    SQLAlchemy type that provides JSON type with transparent encryption and decryption.
    Uses Fernet symmetric encryption internally.
    """

    impl = JSON  # Use JSON type to store encrypted data and metadata

    cache_ok = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fernet = self._get_or_create_fernet()

    def _get_or_create_fernet(self):
        """Get or create Fernet instance using the database config"""
        try:
            key = funiq_ai_config.DB_ENCRYPTION_KEY
            if isinstance(key, str):
                key = key.encode()
            return Fernet(key)
        except Exception as e:
            logger.error(f"Failed to create Fernet instance: {e!s}")
            raise ValueError(f"Invalid encryption key: {e!s}") from e

    def process_bind_param(self, value: Any, dialect) -> dict | None:
        """Encrypt value and convert to database format"""
        if value is None:
            return None

        try:
            # Convert to JSON string
            value_json = json_dumps(value)
            # Encrypt
            encrypted_data = self._fernet.encrypt(value_json.encode("utf-8"))
            # Return dictionary with encrypted data and metadata
            return {"encrypted_data": encrypted_data.decode("utf-8"), "encryption_type": "fernet", "version": "1.0"}
        except Exception as e:
            logger.error(f"Failed to encrypt data: {e!s}")
            raise

    def process_result_value(self, value: dict | None, dialect) -> Any:
        """Decrypt value from database"""
        if value is None:
            return None

        # Handle unencrypted legacy data
        if isinstance(value, dict) and not value.get("encrypted_data"):
            return value

        try:
            encrypted_data = value.get("encrypted_data")
            if not encrypted_data:
                logger.warning("Invalid data format: missing encrypted data")
                return value

            # Decrypt
            decrypted_data = self._fernet.decrypt(encrypted_data.encode("utf-8"))
            # Parse JSON
            return json_loads(decrypted_data.decode("utf-8"))
        except InvalidToken:
            logger.error("Decryption failed: Invalid token or key mismatch")
            # Return None instead of raising exception to prevent application crash
            return None
        except Exception as e:
            logger.error(f"Failed to decrypt data: {e!s}")
            return None


def generate_encryption_key() -> str:
    """
    Generate a new Fernet encryption key
    Returns: Base64 encoded key string
    """
    key = Fernet.generate_key()
    return key.decode()


def generate_protected_key(password: str, salt: bytes | None = None) -> tuple[str, bytes]:
    """
    Generate a Fernet key from a password

    Args:
        password: Password string
        salt: Optional salt value, will be randomly generated if not provided

    Returns:
        tuple: (key string, salt value)
    """
    if salt is None:
        salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key.decode(), salt
