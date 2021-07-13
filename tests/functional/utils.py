import httpx

from tests.functional.conftest import APP_URL


async def send_request(url: str, data: dict, headers: dict = None):
    headers = headers or {}
    client = httpx.AsyncClient(
        base_url=APP_URL,
    )
    resp = await client.post(url=url, json=data, headers=headers)
    await client.aclose()
    return resp
