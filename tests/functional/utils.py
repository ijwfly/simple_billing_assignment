from asyncpg import Pool


class DBHelper:
    def __init__(self, connection_pool: Pool):
        self.connection_pool = connection_pool

    async def clear_db(self):
        sql = """
        delete from billing.transaction;
        delete from billing.wallet;
        """
        await self.connection_pool.execute(sql)

    async def get_wallet(self, wallet_id: int):
        sql = f"select * from billing.wallet where id = {wallet_id}"
        return await self.connection_pool.fetchrow(sql)

    async def get_transaction(self, operation_id: str):
        sql = f"select * from billing.transaction where operation_id = '{operation_id}'"
        return await self.connection_pool.fetchrow(sql)
