from fastapi import HTTPException
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
    code, message = BillingError.invalid_format
    return JSONResponse(
        content={'code': code, 'message': message},
        status_code=200,
    )


async def unhandled_exception_handler(request, exc: Exception):
    return JSONResponse(
        content={'code': 500, 'message': 'Internal server error'},
        status_code=500,
    )


class BillingErrorClass:
    # ошибки протокола
    protocol_error = 'protocol_error'
    # системные ошибки
    system_error = 'system_error'
    # бизнесовые ошибки
    business_domain_error = 'business_domain_error'
    # неизвестные ошибки
    unknown_error = 'unknown_error'


class BillingError:
    invalid_format = (101, 'Invalid query format')

    wallet_already_exists = (201, 'Wallet already exists')
    wallet_not_found = (202, 'Wallet not found')
    same_p2p_wallet = (203, 'Source and target wallets are the same')

    insufficient_funds = (301, 'Insufficient funds')

    @staticmethod
    def get_error_class(error_code):
        if 100 <= error_code <= 199:
            return BillingErrorClass.protocol_error
        elif 200 <= error_code <= 299:
            return BillingErrorClass.system_error
        elif 300 <= error_code <= 399:
            return BillingErrorClass.business_domain_error
        else:
            return BillingErrorClass.unknown_error


InvalidSignatureException = HTTPException(
    status_code=403,
    detail={
        'code': 403,
        'message': 'Invalid signature'
    }
)
