from fastapi import APIRouter
from tortoise.exceptions import IntegrityError, DoesNotExist
from tortoise.transactions import in_transaction

from app.billing.enums import TransactionDirection
from app.billing.exceptions import BillingError, BillingException
from app.billing.models import Wallet, Transaction
from app.billing.validation import (CreateWalletResponse, CreateWalletRequest, WalletCreditResponse,
                                    WalletCreditRequest, WalletDebitResponse, WalletDebitRequest,
                                    WalletP2PTransferResponse, WalletP2PTransferRequest)

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
        raise BillingException(*BillingError.wallet_already_exists)

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
            raise BillingException(*BillingError.wallet_not_found)

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
            raise BillingException(*BillingError.wallet_not_found)

        if wallet.balance < wallet_debit_request.amount:
            raise BillingException(*BillingError.insufficient_funds)

        wallet.balance -= wallet_debit_request.amount
        await wallet.save(using_db=connection)
    return WalletDebitResponse(
        operation_id=wallet_debit_request.operation_id,
    )


@router.post(
    '/wallet_p2p_transfer/',
    summary='Перевод средств на другой кошелёк',
    response_model=WalletP2PTransferResponse,
)
async def billing_wallet_p2p_transfer(
        wallet_p2p_transfer_request: WalletP2PTransferRequest
):
    async with Transaction.context(
        wallet_id=wallet_p2p_transfer_request.from_wallet_id,
        direction=TransactionDirection.debit.value,
        amount=wallet_p2p_transfer_request.amount,
        operation_id=wallet_p2p_transfer_request.operation_id,
    ), Transaction.context(
        wallet_id=wallet_p2p_transfer_request.to_wallet_id,
        direction=TransactionDirection.credit.value,
        amount=wallet_p2p_transfer_request.amount,
        operation_id=wallet_p2p_transfer_request.operation_id,
    ), in_transaction() as connection:
        from_wallet_id = wallet_p2p_transfer_request.from_wallet_id
        to_wallet_id = wallet_p2p_transfer_request.to_wallet_id
        if from_wallet_id == to_wallet_id:
            raise BillingException(*BillingError.same_p2p_wallet)
        try:
            wallets = await Wallet.select_for_update().using_db(connection).filter(
                id__in=[from_wallet_id, to_wallet_id]
            ).order_by('id')
            if len(wallets) < 2:
                raise BillingException(*BillingError.wallet_not_found)
            if wallets[0].id == from_wallet_id:
                from_wallet, to_wallet = wallets
            else:
                to_wallet, from_wallet = wallets
        except DoesNotExist:
            raise BillingException(*BillingError.wallet_not_found)

        if from_wallet.balance < wallet_p2p_transfer_request.amount:
            raise BillingException(*BillingError.insufficient_funds)

        from_wallet.balance -= wallet_p2p_transfer_request.amount
        to_wallet.balance += wallet_p2p_transfer_request.amount
        await from_wallet.save(using_db=connection)
        await to_wallet.save(using_db=connection)
    return WalletP2PTransferResponse(
        operation_id=wallet_p2p_transfer_request.operation_id
    )
