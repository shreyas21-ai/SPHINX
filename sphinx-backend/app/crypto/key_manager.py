import base64
import os
from flask import current_app


class KeyManager:
    """Manages cryptographic key retrieval and validation from application context."""

    @staticmethod
    def get_aes_key() -> bytes:
        """Retrieves and decodes the 256-bit AES master key from app config."""
        key_str = current_app.config.get('SPHINX_AES_SECRET_KEY')
        if not key_str:
            raise ValueError("SPHINX_AES_SECRET_KEY is missing in configuration.")

        try:
            raw_key = base64.b64decode(key_str)
            if len(raw_key) != 32:
                raise ValueError(f"AES-256 key must be exactly 32 bytes (256 bits), got {len(raw_key)} bytes.")
            return raw_key
        except Exception as e:
            raise ValueError(f"Invalid AES key format: {str(e)}")

    @staticmethod
    def get_hmac_key() -> bytes:
        """Retrieves and decodes the HMAC key from app config."""
        key_str = current_app.config.get('SPHINX_HMAC_SECRET_KEY')
        if not key_str:
            raise ValueError("SPHINX_HMAC_SECRET_KEY is missing in configuration.")

        try:
            raw_key = base64.b64decode(key_str)
            if len(raw_key) < 16:
                raise ValueError("HMAC key must be at least 16 bytes long.")
            return raw_key
        except Exception as e:
            raise ValueError(f"Invalid HMAC key format: {str(e)}")
