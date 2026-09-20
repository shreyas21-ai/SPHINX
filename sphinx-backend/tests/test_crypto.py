from app.crypto.aes_cipher import AESCipher
from app.crypto.hmac_indexer import HMACSearchIndexer


def test_aes_encryption_decryption(app):
    with app.app_context():
        plaintext = "Patient suffers from Type 2 Diabetes Mellitus"

        ciphertext1 = AESCipher.encrypt(plaintext)
        ciphertext2 = AESCipher.encrypt(plaintext)

        # Semantic security test: identical plaintext must yield different ciphertexts due to random nonces
        assert ciphertext1 != ciphertext2

        # Roundtrip decryption
        decrypted1 = AESCipher.decrypt(ciphertext1)
        decrypted2 = AESCipher.decrypt(ciphertext2)

        assert decrypted1 == plaintext
        assert decrypted2 == plaintext


def test_hmac_search_indexing(app):
    with app.app_context():
        disease = "Diabetes Mellitus"

        # Exact token generation
        exact_token = HMACSearchIndexer.generate_exact_token('disease', disease)
        assert exact_token is not None
        assert len(exact_token) == 64  # SHA-256 hex string

        # Deterministic HMAC exact match
        exact_token_again = HMACSearchIndexer.generate_exact_token('disease', disease)
        assert exact_token == exact_token_again

        # Case and whitespace normalization test
        exact_token_normalized = HMACSearchIndexer.generate_exact_token('disease', "  diabetes   mellitus  ")
        assert exact_token == exact_token_normalized

        # Substring n-gram tokens test
        ngrams = HMACSearchIndexer.generate_ngram_tokens('disease', "Diab")
        assert len(ngrams) > 0
