from contextlib import asynccontextmanager
from datetime import datetime

from tortoise import Model, fields

from app.billing.enums import TransactionStatus, TransactionDirection
from app.billing.exceptions import BillingException


class Transaction(Model):
    id = fields.BigIntField(pk=True)
    operation_id = fields.TextField()
    wallet_id = fields.BigIntField()
    status = fields.CharEnumField(enum_type=TransactionStatus, default=TransactionStatus.registered)
    direction = fields.CharEnumField(enum_type=TransactionDirection)
    amount = fields.BigIntField(default=0)
    cdate = fields.DatetimeField(default=lambda: datetime.now().astimezone())
    response_code = fields.IntField()

    @classmethod
    @asynccontextmanager
    async def context(cls, **kwargs):
        transaction = await cls.create(**kwargs)
        try:
            yield transaction
            transaction.status = TransactionStatus.completed
            transaction.response_code = 0
        except BillingException as exc:
            transaction.status = TransactionStatus.error
            transaction.response_code = exc.code
            raise
        except:
            transaction.status = TransactionStatus.error
            raise
        finally:
            await transaction.save()

class Wallet(Model):
    id = fields.BigIntField(pk=True)
    balance = fields.BigIntField(default=0)
    user_id = fields.BigIntField()
