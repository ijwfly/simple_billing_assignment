from datetime import datetime

from tortoise import Model, fields

from app.billing.enums import TransactionStatus, TransactionDirection


class Transaction(Model):
    id = fields.BigIntField(pk=True)
    operation_id = fields.TextField()
    wallet_id = fields.BigIntField()
    status = fields.CharEnumField(enum_type=TransactionStatus, default=TransactionStatus.registered)
    direction = fields.CharEnumField(enum_type=TransactionDirection)
    amount = fields.BigIntField(default=0)
    cdate = fields.DatetimeField(default=lambda: datetime.now().astimezone())


class Wallet(Model):
    id = fields.BigIntField(pk=True)
    balance = fields.BigIntField(default=0)
    user_id = fields.BigIntField()
