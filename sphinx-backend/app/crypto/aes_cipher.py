import base64
import os
from typing import Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.crypto.key_manager import KeyManager


class AESCipher:
    """Enterprise AES-256-GCM Authenticated Field Encryption Cipher."""

    @staticmethod
    def encrypt(plaintext: Optional[str], key: Optional[bytes] = None) -> Optional[str]:
        """
        Encrypts plaintext using AES-256-GCM.
        Generates a unique 96-bit (12-byte) initialization vector (nonce) for every encryption.
        Returns base64 encoded payload containing nonce + ciphertext + tag.
        """
        if plaintext is None or plaintext == "":
            return plaintext

        if key is None:
            key = KeyManager.get_aes_key()

        aesgcm = AESGCM(key)
        nonce = os.urandom(12)  # 96-bit nonce standard for AES-GCM
        plaintext_bytes = plaintext.encode('utf-8')

        # AESGCM encrypt returns ciphertext concatenated with tag
        encrypted_bytes = aesgcm.encrypt(nonce, plaintext_bytes, associated_data=None)

        payload = nonce + encrypted_bytes
        return base64.b64encode(payload).decode('utf-8')

    @staticmethod
    def decrypt(ciphertext_b64: Optional[str], key: Optional[bytes] = None) -> Optional[str]:
        """
        Decrypts base64 encoded AES-256-GCM ciphertext payload.
        Extracts nonce, verifies authenticity tag, and decrypts payload.
        """
        if ciphertext_b64 is None or ciphertext_b64 == "":
            return ciphertext_b64

        if key is None:
            key = KeyManager.get_aes_key()

        try:
            payload = base64.b64decode(ciphertext_b64.encode('utf-8'))
            if len(payload) < 28:  # 12-byte nonce + 16-byte minimum tag/ciphertext
                raise ValueError("Ciphertext payload is corrupted or truncated.")

            nonce = payload[:12]
            encrypted_bytes = payload[12:]

            aesgcm = AESGCM(key)
            decrypted_bytes = aesgcm.decrypt(nonce, encrypted_bytes, associated_data=None)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            # Handle decryption error safely
            raise ValueError(f"Decryption failed or invalid key/tag: {str(e)}")
