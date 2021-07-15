from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse


class BillingException(Exception):
    def __init__(self, error_code, message):
        super().__init__(message)
        self.code = error_code


def billing_exception_handler(request, exc: BillingException):
    return JSONResponse(
        content={'code': exc.code, 'message': str(exc)},
        status_code=200,
    )


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


class BillingErrors:
    wallet_already_exists = (201, 'Wallet already exists')
    wallet_not_found = (202, 'Wallet not found')
    # TODO: переместить в отдельный класс ошибок для корректной обработки (статус транзакции должен быть declined)
    insufficient_funds = (203, 'Insufficient funds')
