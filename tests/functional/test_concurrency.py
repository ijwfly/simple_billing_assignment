import asyncio
from multiprocessing import cpu_count
from random import randint, choice
from uuid import uuid4

import pytest

from tests.functional.utils import DBHelper, chunks


@pytest.mark.asyncio
class TestConcurrency:
    create_wallet_url = '/billing/v1/create_wallet/'
    wallet_credit_url = '/billing/v1/wallet_credit/'
    wallet_debit_url = '/billing/v1/wallet_debit/'
    p2p_url = '/billing/v1/wallet_p2p_transfer/'

    concurrency = cpu_count() * 2
    wallets_count = cpu_count()
    actions_count = 1000

    wallet_balance = 100000
    operation_amount = 100

    money_in_system = None
    wallets = []

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

    async def create_wallets(self, wallets_num, send_request):
        result = []
        concurrency = self.concurrency if self.concurrency < wallets_num else wallets_num
        while len(result) < wallets_num:
            coros = []
            for _ in range(concurrency):
                user_id = randint(0, 999999999)
                operation_id = str(uuid4())
                coros.append(self.create_wallet(user_id, operation_id, send_request))
            wallets = await asyncio.gather(*coros)
            result += wallets
        return result

    async def wallet_debit(self, send_request):
        operation_id = str(uuid4())
        wallet_id = choice(self.wallets)
        data = {
            'wallet_id': wallet_id,
            'operation_id': operation_id,
            'amount': self.operation_amount,
        }
        resp = await send_request(self.wallet_debit_url, data)
        assert resp.status_code == 200
        resp_data = resp.json()
        if resp_data['code'] == 0:
            self.money_in_system -= self.operation_amount

    async def wallet_credit(self, send_request):
        operation_id = str(uuid4())
        wallet_id = choice(self.wallets)
        data = {
            'wallet_id': wallet_id,
            'operation_id': operation_id,
            'amount': self.operation_amount,
        }
        resp = await send_request(self.wallet_credit_url, data)
        assert resp.status_code == 200
        resp_data = resp.json()
        if resp_data['code'] == 0:
            self.money_in_system += self.operation_amount

    async def p2p_transfer(self, send_request):
        operation_id = str(uuid4())
        from_wallet_id = choice(self.wallets)
        to_wallet_id = choice(self.wallets)
        data = {
            'from_wallet_id': from_wallet_id,
            'to_wallet_id': to_wallet_id,
            'operation_id': operation_id,
            'amount': self.operation_amount,
        }
        resp = await send_request(self.p2p_url, data)
        assert resp.status_code == 200

    async def test_concurrent_write(self, db_helper: DBHelper, send_request):
        actions = [
            self.wallet_credit,
            self.wallet_debit,
            self.p2p_transfer
        ]
        self.wallets = await self.create_wallets(self.wallets_count, send_request)
        for wallet_id in self.wallets:
            await db_helper.change_wallet_balance(wallet_id, self.wallet_balance)
        self.money_in_system = await db_helper.get_sum_of_money()

        coros = []
        for _ in range(self.actions_count):
            action = choice(actions)
            coros.append(action(send_request))
        for coros_chunk in chunks(coros, self.concurrency):
            await asyncio.gather(*coros_chunk)

        assert self.money_in_system == await db_helper.get_sum_of_money()
