import pytest

from tests.functional.utils import send_request


@pytest.mark.asyncio
class TestCreateWallet:
    url = '/billing/v1/create_wallet/'

    async def test_success(self, operation_id):
        data = {
            'user_id': 12345678,
            'operation_id': operation_id,
        }
        resp = await send_request(self.url, data)

        assert resp.status_code == 200
        resp_data = resp.json()
        assert resp_data['code'] == 0
        assert resp_data['operation_id'] == operation_id
        assert resp_data['wallet_id'] >= 0
