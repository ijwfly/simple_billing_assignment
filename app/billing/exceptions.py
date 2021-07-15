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


class BillingErrorClass:
    # системные ошибки
    system_error = 'system_error'
    # бизнесовые ошибки
    business_domain_error = 'business_domain_error'
    # неизвестные ошибки
    unknown_error = 'unknown_error'


class BillingError:
    wallet_already_exists = (201, 'Wallet already exists')
    wallet_not_found = (202, 'Wallet not found')

    insufficient_funds = (301, 'Insufficient funds')

    @staticmethod
    def get_error_class(error_code):
        if 200 <= error_code <= 299:
            return BillingErrorClass.system_error
        elif 300 <= error_code <= 399:
            return BillingErrorClass.business_domain_error
        else:
            return BillingErrorClass.unknown_error
