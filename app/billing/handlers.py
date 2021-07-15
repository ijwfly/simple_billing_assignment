from fastapi import APIRouter
from tortoise.exceptions import IntegrityError, DoesNotExist
from tortoise.transactions import in_transaction

from app.billing.enums import TransactionDirection
from app.billing.exceptions import BillingErrors, BillingException
from app.billing.models import Wallet, Transaction
from app.billing.validation import (CreateWalletResponse, CreateWalletRequest, WalletCreditResponse,
                                    WalletCreditRequest, WalletDebitResponse, WalletDebitRequest)

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
        raise BillingException(*BillingErrors.wallet_already_exists)

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
    async with Transaction.context(
            direction=TransactionDirection.credit,
            wallet_id=wallet_credit_request.wallet_id,
            amount=wallet_credit_request.amount,
            operation_id=wallet_credit_request.operation_id,
    ), in_transaction() as connection:
        try:
            wallet = await Wallet.select_for_update().using_db(connection).get(id=wallet_credit_request.wallet_id)
        except DoesNotExist:
            raise BillingException(*BillingErrors.wallet_not_found)

        wallet.balance += wallet_credit_request.amount
        await wallet.save(using_db=connection)
    return WalletCreditResponse(
        operation_id=wallet_credit_request.operation_id,
    )


@router.post(
    '/wallet_debit/',
    summary='Списание средств с кошелька',
    response_model=WalletDebitResponse,
)
async def billing_wallet_debit(
        wallet_debit_request: WalletDebitRequest
):
    async with Transaction.context(
            wallet_id=wallet_debit_request.wallet_id,
            direction=TransactionDirection.debit.value,
            amount=wallet_debit_request.amount,
            operation_id=wallet_debit_request.operation_id,
    ), in_transaction() as connection:
        try:
            wallet = await Wallet.select_for_update().using_db(connection).get(id=wallet_debit_request.wallet_id)
        except DoesNotExist:
            raise BillingException(*BillingErrors.wallet_not_found)

        if wallet.balance < wallet_debit_request.amount:
            raise BillingException(*BillingErrors.insufficient_funds)

        wallet.balance -= wallet_debit_request.amount
        await wallet.save(using_db=connection)
    return WalletCreditResponse(
        operation_id=wallet_debit_request.operation_id,
    )
