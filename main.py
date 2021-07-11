import uvicorn
from fastapi import FastAPI

from app.billing.router import router as billing_router
from app.config import get_app_config, AppConfig


def build_app(config: AppConfig):
    app = FastAPI(
        debug=config.server.debug,
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
