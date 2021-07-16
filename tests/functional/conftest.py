import asyncio
import json
import uuid
from base64 import b64encode

import asyncpg
import httpx
import pytest

from app.auth.hmac_signer import HMACSigner
from app.config import get_app_config, AppConfig
from tests.functional.utils import DBHelper

APP_URL = 'http://app:8080'


@pytest.fixture(scope='session')
async def send_request(app_config):
    client = httpx.AsyncClient(base_url=APP_URL)
    async def _send_request(url: str, data: dict, headers: dict = None):
        headers = headers or {}
        if app_config.auth.check:
            signer = HMACSigner(app_config.auth.hmac_shared_key)
            headers['X-Signature'] = b64encode(signer.create_signature(json.dumps(data).encode()))
        return await client.post(url=url, json=data, headers=headers)
    yield _send_request
    await client.aclose()


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
