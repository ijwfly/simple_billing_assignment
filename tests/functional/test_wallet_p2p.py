from random import randint
from uuid import uuid4

import pytest

from app.billing.enums import TransactionDirection, TransactionStatus


@pytest.mark.asyncio
class TestWalletDebit:
    create_wallet_url = '/billing/v1/create_wallet/'
    url = '/billing/v1/wallet_p2p_transfer/'

    async def create_wallet(self, user_id, operation_id, send_request):
        data = {
            'user_id': user_id,
            'operation_id': operation_id,
        }
        resp = await send_request(self.create_wallet_url, data)
        assert resp.status_code == 200
        resp_data = resp.json()
        assert resp_data['code'] == 0
        assert resp_data['operation_id'] == operation_id
        return resp_data['wallet_id']

    @pytest.mark.parametrize(
        'from_balance, amount, from_balance_result, to_balance_result, resp_code, trans_status',
        [
            (5000, 100, 5000-100, 100, 0, TransactionStatus.completed.value),
            (5000, 5500, 5000, 0, 203, TransactionStatus.error.value),
        ]
    )
    async def test_straightforward(self, db_helper, send_request, from_balance, amount, resp_code,
                                   from_balance_result, to_balance_result, trans_status):
        from_operation_id = str(uuid4())
        from_user_id = randint(0, 99999999)
        from_wallet_id = await self.create_wallet(from_user_id, from_operation_id, send_request)

        to_operation_id = str(uuid4())
        to_user_id = randint(0, 99999999)
        to_wallet_id = await self.create_wallet(to_user_id, to_operation_id, send_request)

        await db_helper.change_wallet_balance(from_wallet_id, from_balance)

        operation_id = str(uuid4())
        data = {
            'from_wallet_id': from_wallet_id,
            'to_wallet_id': to_wallet_id,
            'operation_id': operation_id,
            'amount': amount,
        }
        resp = await send_request(self.url, data)

        assert resp.status_code == 200
        resp_data = resp.json()
        assert resp_data['code'] == resp_code

        from_wallet = await db_helper.get_wallet(from_wallet_id)
        assert from_wallet['balance'] == from_balance_result
        to_wallet = await db_helper.get_wallet(to_wallet_id)
        assert to_wallet['balance'] == to_balance_result

        transactions = await db_helper.get_multiple_transactions(operation_id)
        debit_transaction = [t for t in transactions if t['direction'] == TransactionDirection.debit.value][0]
        assert debit_transaction['operation_id'] == operation_id
        assert debit_transaction['status'] == trans_status
        assert debit_transaction['amount'] == amount
        assert debit_transaction['wallet_id'] == from_wallet_id
        assert debit_transaction['response_code'] == resp_code

        credit_transaction = [t for t in transactions if t['direction'] == TransactionDirection.credit.value][0]
        assert credit_transaction['operation_id'] == operation_id
        assert credit_transaction['status'] == trans_status
        assert credit_transaction['amount'] == amount
        assert credit_transaction['wallet_id'] == to_wallet_id
        assert credit_transaction['response_code'] == resp_code

    async def test_no_wallet(self, db_helper, send_request):
        from_operation_id = str(uuid4())
        from_user_id = randint(0, 99999999)
        from_wallet_id = await self.create_wallet(from_user_id, from_operation_id, send_request)

        new_balance = 5000
        await db_helper.change_wallet_balance(from_wallet_id, new_balance)

        operation_id = str(uuid4())
        random_wallet_id = randint(0, 999999999)
        amount = 100
        data = {
            'from_wallet_id': from_wallet_id,
            'to_wallet_id': random_wallet_id,
            'operation_id': operation_id,
            'amount': amount,
        }
        resp = await send_request(self.url, data)
        assert resp.status_code == 200
        resp_data = resp.json()
        assert resp_data['code'] == 202

        transactions = await db_helper.get_multiple_transactions(operation_id)
        debit_transaction = [t for t in transactions if t['direction'] == TransactionDirection.debit.value][0]
        assert debit_transaction['operation_id'] == operation_id
        assert debit_transaction['status'] == TransactionStatus.error.value
        assert debit_transaction['amount'] == amount
        assert debit_transaction['wallet_id'] == from_wallet_id

        credit_transaction = [t for t in transactions if t['direction'] == TransactionDirection.credit.value][0]
        assert credit_transaction['operation_id'] == operation_id
        assert credit_transaction['status'] == TransactionStatus.error.value
        assert credit_transaction['amount'] == amount
        assert credit_transaction['wallet_id'] == random_wallet_id
