import hmac


class HMACSigner:
    def __init__(self, hmac_shared_key: str):
        self.hmac_shared_key = hmac_shared_key

    def create_signature(self, data: bytes) -> bytes:
        return hmac.new(self.hmac_shared_key.encode(), data, 'sha256').digest()

    def check_signature(self, data: bytes, signature: bytes) -> bool:
        calculated_signature = self.create_signature(data)
        return hmac.compare_digest(calculated_signature, signature)
