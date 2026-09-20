import hmac
import hashlib
import re
from typing import List, Tuple, Optional
from app.crypto.key_manager import KeyManager


class HMACSearchIndexer:
    """
    Searchable Encryption Engine based on Cryptographic HMAC Blind Indexing.
    Supports Exact Match hashing and Character N-Gram hashing for secure Substring Search.
    """

    @staticmethod
    def _normalize(text: str) -> str:
        """Normalizes text by lowercasing and trimming whitespace."""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text.strip().lower())

    @classmethod
    def generate_exact_token(cls, field_name: str, value: str, hmac_key: Optional[bytes] = None) -> Optional[str]:
        """Generates HMAC-SHA256 token for exact field value match."""
        normalized = cls._normalize(value)
        if not normalized:
            return None

        if hmac_key is None:
            hmac_key = KeyManager.get_hmac_key()

        token_input = f"EXACT:{field_name.lower()}:{normalized}".encode('utf-8')
        return hmac.new(hmac_key, token_input, hashlib.sha256).hexdigest()

    @classmethod
    def generate_ngram_tokens(cls, field_name: str, value: str, min_n: int = 3, max_n: int = 4, hmac_key: Optional[bytes] = None) -> List[str]:
        """
        Generates character n-gram HMAC tokens for substring search.
        Breaks down input into sliding character windows of length min_n to max_n.
        """
        normalized = cls._normalize(value)
        if not normalized:
            return []

        if hmac_key is None:
            hmac_key = KeyManager.get_hmac_key()

        tokens = set()
        # Clean non-alphanumeric for cleaner n-grams while preserving space marker
        clean_text = f" {normalized} "
        length = len(clean_text)

        for n in range(min_n, max_n + 1):
            if length < n:
                continue
            for i in range(length - n + 1):
                ngram = clean_text[i:i + n]
                if ngram.strip():  # ignore pure space ngrams
                    token_input = f"NGRAM:{field_name.lower()}:{ngram}".encode('utf-8')
                    token_hash = hmac.new(hmac_key, token_input, hashlib.sha256).hexdigest()
                    tokens.add(token_hash)

        return list(tokens)

    @classmethod
    def generate_all_index_entries(cls, field_name: str, value: str, hmac_key: Optional[bytes] = None) -> List[Tuple[str, str]]:
        """
        Generates all cryptographic search index tuples (token_hash, token_type)
        for a given field and value.
        """
        entries = []
        if not value:
            return entries

        exact_token = cls.generate_exact_token(field_name, value, hmac_key=hmac_key)
        if exact_token:
            entries.append((exact_token, 'EXACT'))

        ngram_tokens = cls.generate_ngram_tokens(field_name, value, hmac_key=hmac_key)
        for token in ngram_tokens:
            entries.append((token, 'NGRAM'))

        return entries
