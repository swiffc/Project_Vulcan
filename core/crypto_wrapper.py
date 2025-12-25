"""
Crypto Wrapper
==============
Handles simple encryption for stored API keys and secrets.
Uses Fernet (symmetric encryption).
"""

import os
import logging
from cryptography.fernet import Fernet

logger = logging.getLogger("vulcan.core.crypto")


def _get_or_generate_key() -> bytes:
    """
    Get encryption key from environment or generate one.
    In production, VULCAN_SECRET_KEY must be set.
    In development, generates and caches a key in .vulcan_key file.
    """
    env_key = os.getenv("VULCAN_SECRET_KEY", "").encode()
    if env_key:
        return env_key

    # Development only: use a local key file
    key_file = os.path.join(os.path.dirname(__file__), "..", ".vulcan_key")
    key_file = os.path.abspath(key_file)

    if os.path.exists(key_file):
        with open(key_file, "rb") as f:
            return f.read().strip()

    # Generate new key for development
    new_key = Fernet.generate_key()
    try:
        with open(key_file, "wb") as f:
            f.write(new_key)
        logger.warning(
            f"Generated new encryption key for development. "
            f"Set VULCAN_SECRET_KEY in production."
        )
    except OSError:
        logger.warning("Could not save key file, using ephemeral key")

    return new_key


class CryptoWrapper:
    """Simple wrapper for encrypting secrets at rest."""

    def __init__(self, key: bytes = None):
        self.key = key or _get_or_generate_key()
        try:
            self.cipher = Fernet(self.key)
        except Exception as e:
            logger.error(f"Invalid encryption key format: {e}")
            raise ValueError(
                "Invalid VULCAN_SECRET_KEY. Must be a valid Fernet key. "
                "Generate one with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            )

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string."""
        if not plaintext:
            return ""
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a string."""
        if not ciphertext:
            return ""
        try:
            return self.cipher.decrypt(ciphertext.encode()).decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError("Invalid secret")


# Singleton
_crypto = CryptoWrapper()


def get_crypto() -> CryptoWrapper:
    return _crypto
