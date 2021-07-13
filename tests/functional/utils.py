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
        return await self.connection_pool.fetch(sql)
