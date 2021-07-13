import asyncio
import uuid

import asyncpg
import httpx
import pytest

from app.config import get_app_config, AppConfig
from tests.functional.utils import DBHelper

APP_URL = 'http://app:8080'


@pytest.fixture
def send_request():
    async def _send_request(url: str, data: dict, headers: dict = None):
        headers = headers or {}
        async with httpx.AsyncClient(base_url=APP_URL) as client:
            return await client.post(url=url, json=data, headers=headers)
    return _send_request


@pytest.fixture
def operation_id():
    return str(uuid.uuid4())


@pytest.fixture(scope='session')
def app_config() -> AppConfig:
    return get_app_config()


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def db_helper(app_config, event_loop):
    db = app_config.db
    dsn = f'postgres://{db.user}:{db.password}@{db.host}:{db.port}/{db.database}'
    async with asyncpg.create_pool(dsn=dsn) as pool:
        yield DBHelper(pool)
