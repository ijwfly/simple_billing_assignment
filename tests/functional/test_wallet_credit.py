from uuid import uuid4

import pytest

from app.billing.enums import TransactionDirection, TransactionStatus


@pytest.mark.asyncio
class TestWalletCredit:
    create_wallet_url = '/billing/v1/create_wallet/'
    url = '/billing/v1/wallet_credit/'

    async def test_success(self, operation_id, db_helper, send_request):
        await db_helper.clear_db()
        user_id = 12345678
        data = {
            'user_id': user_id,
            'operation_id': operation_id,
        }
        resp = await send_request(self.create_wallet_url, data)

        assert resp.status_code == 200
        resp_data = resp.json()
        assert resp_data['code'] == 0
        assert resp_data['operation_id'] == operation_id

        wallet_id = resp_data['wallet_id']
        operation_id = str(uuid4())
        amount = 100
        data = {
            'wallet_id': wallet_id,
            'operation_id': operation_id,
            'amount': amount,
        }
        resp = await send_request(self.url, data)

        assert resp.status_code == 200
        resp_data = resp.json()
        assert resp_data['code'] == 0
        assert resp_data['operation_id'] == operation_id
        wallet = await db_helper.get_wallet(wallet_id)
        assert wallet['balance'] == amount

        transaction = await db_helper.get_transaction(operation_id)
        assert transaction['direction'] == TransactionDirection.credit.value
        assert transaction['operation_id'] == operation_id
        assert transaction['status'] == TransactionStatus.completed.value
        assert transaction['amount'] == amount
        assert transaction['wallet_id'] == wallet_id
