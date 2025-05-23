from hmac import new
from hashlib import sha256


class HMACSigner:
    _key: bytes

    def __init__(self, /, hex_key: str):
        self._key = bytes.fromhex(hex_key)

    def __call__(self, message: bytes) -> str:
        hmac = new(self._key, message, sha256)
        signature = hmac.hexdigest()
        return signature
