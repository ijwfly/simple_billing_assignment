import pydantic


class BaseBillingRequestModel(pydantic.BaseModel):
    operation_id: str


class BaseBillingResponseModel(pydantic.BaseModel):
    operation_id: str
    code: int = 0
    message: str = "Success"


class CreateWalletRequest(BaseBillingRequestModel):
    user_id: int


class CreateWalletResponse(BaseBillingResponseModel):
    wallet_id: int
