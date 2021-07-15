from base64 import b64decode

from fastapi import Request, Depends
from fastapi.security import APIKeyHeader

from app.auth.hmac_signer import HMACSigner
from app.billing.exceptions import InvalidSignatureException


class HMACChecker:
    def __init__(self, hmac_signer: HMACSigner):
        self.hmac_signer = hmac_signer

    async def __call__(
            self,
            request: Request,
            signature: str = Depends(APIKeyHeader(name='X-Signature', auto_error=False)),
    ):
        signature = b64decode(signature)
        if not signature or not self.hmac_signer.check_signature(
            await request.body(),
            signature=signature,
        ):
            raise InvalidSignatureException
