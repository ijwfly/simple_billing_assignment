import json
import os
import pathlib
from functools import lru_cache

import pydantic

BASE_DIR = pathlib.Path(__file__).parent.parent


class ServerConfig(pydantic.BaseModel):
    port: int
    host: str
    debug: bool = False


class AuthConfig(pydantic.BaseModel):
    check: bool = True
    hmac_shared_key: str


class DatabaseConfig(pydantic.BaseModel):
    host: str
    port: int = 5432
    user: str
    password: str
    database: str


class AppConfig(pydantic.BaseModel):
    server: ServerConfig
    auth: AuthConfig
    db: DatabaseConfig


@lru_cache(1)
def get_app_config() -> AppConfig:
    app_config_path = os.environ.get('APP_CONFIG', None)
    if app_config_path is None:
        app_config_path = BASE_DIR / 'debug_config.json'
    with open(app_config_path, 'r') as config_file:
        config_raw = config_file.read()
    return AppConfig(**json.loads(config_raw))
