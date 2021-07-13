from fastapi import APIRouter, Request
from tortoise.exceptions import IntegrityError

from app.billing.exceptions import generate_common_error, CommonErrors
from app.billing.models import Wallet
from app.billing.validation import CreateWalletResponse, CreateWalletRequest

router = APIRouter()


@router.post(
    '/create_wallet/',
    summary='Создание кошелька для пользователя (существующего в другой системе)',
    response_model=CreateWalletResponse
)
async def billing_create_wallet(
        wallet_data: CreateWalletRequest
):
    try:
        wallet = await Wallet.create(user_id=wallet_data.user_id)
    except IntegrityError:
        return generate_common_error(*CommonErrors.wallet_already_exists)

    return CreateWalletResponse(
        operation_id=wallet_data.operation_id,
        wallet_id=wallet.id,
    )
