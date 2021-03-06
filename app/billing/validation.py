import pydantic
from pydantic import PositiveInt, NonNegativeInt


class BaseBillingRequestModel(pydantic.BaseModel):
    operation_id: str


class BaseBillingResponseModel(pydantic.BaseModel):
    operation_id: str
    code: NonNegativeInt = 0
    message: str = "Success"


class CreateWalletRequest(BaseBillingRequestModel):
    user_id: NonNegativeInt


class CreateWalletResponse(BaseBillingResponseModel):
    wallet_id: NonNegativeInt


class WalletCreditRequest(BaseBillingRequestModel):
    wallet_id: NonNegativeInt
    amount: PositiveInt


class WalletCreditResponse(BaseBillingResponseModel):
    pass


class WalletDebitRequest(BaseBillingRequestModel):
    wallet_id: NonNegativeInt
    amount: PositiveInt


class WalletDebitResponse(BaseBillingResponseModel):
    pass


class WalletP2PTransferRequest(BaseBillingRequestModel):
    from_wallet_id: NonNegativeInt
    to_wallet_id: NonNegativeInt
    amount: PositiveInt


class WalletP2PTransferResponse(BaseBillingResponseModel):
    pass
