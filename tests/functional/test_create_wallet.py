from uuid import uuid4

import pytest


@pytest.mark.asyncio
class TestCreateWallet:
    url = '/billing/v1/create_wallet/'

    async def test_success(self, operation_id, db_helper, send_request):
        await db_helper.clear_db()
        user_id = 12345678
        data = {
            'user_id': user_id,
            'operation_id': operation_id,
        }
        resp = await send_request(self.url, data)

        assert resp.status_code == 200
        resp_data = resp.json()
        assert resp_data['code'] == 0
        assert resp_data['operation_id'] == operation_id

        wallet_id = resp_data['wallet_id']

        wallet = await db_helper.get_wallet(wallet_id)
        assert wallet['balance'] == 0
        assert wallet['user_id'] == user_id

    async def test_already_exists(self, operation_id, db_helper, send_request):
        await db_helper.clear_db()

        user_id = 12345678
        data = {
            'user_id': user_id,
            'operation_id': operation_id,
        }
        resp = await send_request(self.url, data)

        assert resp.status_code == 200
        resp_data = resp.json()
        assert resp_data['code'] == 0
        assert resp_data['operation_id'] == operation_id

        data['operation_id'] = str(uuid4())
        resp = await send_request(self.url, data)
        assert resp.status_code == 200
        resp_data = resp.json()
        assert resp_data['code'] == 201
