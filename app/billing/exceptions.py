from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse


async def request_validation_error_handler(request, exc: RequestValidationError):
    return JSONResponse(
        content={'code': 101, 'message': 'Invalid query format'},
        status_code=200,
    )


async def unhandled_exception_handler(request, exc: Exception):
    return JSONResponse(
        content={'code': 500, 'message': 'Internal server error'},
        status_code=500,
    )


def generate_common_error(code, message):
    return JSONResponse(
        content={'code': code, 'message': message},
        status_code=200,
    )


class CommonErrors:
    wallet_already_exists = (201, 'Wallet already exists')
