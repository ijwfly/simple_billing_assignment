import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from tortoise import Tortoise

from app.billing.exceptions import (request_validation_error_handler, unhandled_exception_handler,
                                    billing_exception_handler, BillingException)
from app.billing.handlers import router as billing_router
from app.config import get_app_config, AppConfig


def build_app(config: AppConfig):
    applications = ['billing']

    async def db_connect():
        await Tortoise.init(
            {
                'connections': {
                    application: {
                        'engine': 'tortoise.backends.asyncpg',
                        'credentials': {
                            'host': config.db.host,
                            'port': config.db.port,
                            'user': config.db.user,
                            'password': config.db.password,
                            'database': config.db.database,
                            'schema': application,
                        }
                    }
                    for application in applications
                },
                'apps': {
                    application: {
                        'models': [f'app.{application}.models'],
                        'default_connection': application
                    }
                    for application in applications
                },
            }
        )
        await Tortoise.generate_schemas()

    async def db_disconnect():
        await Tortoise.close_connections()

    app = FastAPI(
        debug=config.server.debug,
        on_startup=[
            db_connect,
        ],
        on_shutdown=[
            db_disconnect
        ],
        exception_handlers={
            RequestValidationError: request_validation_error_handler,
            BillingException: billing_exception_handler,
            Exception: unhandled_exception_handler,
        },
    )
    app.include_router(
        billing_router,
        prefix='/billing/v1',
    )
    return app


def main():
    config = get_app_config()
    app = build_app(config)
    uvicorn.run(
        app,
        host=config.server.host,
        port=config.server.port,
    )


if __name__ == '__main__':
    main()
