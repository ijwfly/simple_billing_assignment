from fastapi import APIRouter, Request
from tortoise.exceptions import IntegrityError, DoesNotExist
from tortoise.transactions import in_transaction

from app.billing.enums import TransactionStatus, TransactionDirection
from app.billing.exceptions import generate_common_error, CommonErrors
from app.billing.models import Wallet, Transaction
from app.billing.validation import CreateWalletResponse, CreateWalletRequest, WalletCreditResponse, WalletCreditRequest

router = APIRouter()


@router.post(
    '/create_wallet/',
    summary='Создание кошелька для пользователя (существующего в другой системе)',
    response_model=CreateWalletResponse,
)
async def billing_create_wallet(
        create_wallet_request: CreateWalletRequest
):
    try:
        wallet = await Wallet.create(user_id=create_wallet_request.user_id)
    except IntegrityError:
        return generate_common_error(*CommonErrors.wallet_already_exists)

    return CreateWalletResponse(
        operation_id=create_wallet_request.operation_id,
        wallet_id=wallet.id,
    )


@router.post(
    '/wallet_credit/',
    summary='Зачисление средств на кошелёк',
    response_model=WalletCreditResponse,
)
async def billing_wallet_credit(
        wallet_credit_request: WalletCreditRequest
):
    async with in_transaction():
        try:
            wallet = await Wallet.select_for_update().get(id=wallet_credit_request.wallet_id)
        except DoesNotExist:
            return generate_common_error(*CommonErrors.wallet_not_found)
        transaction = await Transaction.create(
            wallet_id=wallet.id,
            status=TransactionStatus.registered.value,
            direction=TransactionDirection.credit.value,
            amount=wallet_credit_request.amount,
            operation_id=wallet_credit_request.operation_id,
        )
        wallet.balance += wallet_credit_request.amount
        transaction.status = TransactionStatus.completed
        await wallet.save()
        await transaction.save()
    return WalletCreditResponse(
        operation_id=wallet_credit_request.operation_id,
    )
