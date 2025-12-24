"""
Crypto Wrapper
==============
Handles simple encryption for stored API keys and secrets.
Uses Fernet (symmetric encryption).
"""

import os
import logging
from cryptography.fernet import Fernet
from typing import Optional

logger = logging.getLogger("vulcan.core.crypto")

# Default key for development (In production, load from environment)
# WARNING: This is a placeholder key. Real deployment should generate this once.
FALLBACK_KEY = b"G6uB8_fD4g5hJ7kL9_mN2oP3qR5sT8uV1wX4yZ7aB9c="


class CryptoWrapper:
    """Simple wrapper for encrypting secrets at rest."""

    def __init__(self, key: bytes = None):
        self.key = key or os.getenv("VULCAN_SECRET_KEY", "").encode() or FALLBACK_KEY
        try:
            self.cipher = Fernet(self.key)
        except Exception:
            # Fallback if key is invalid
            logger.warning("Invalid encryption key, using fallback")
            self.cipher = Fernet(FALLBACK_KEY)

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
