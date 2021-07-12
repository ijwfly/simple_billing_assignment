from tortoise import Model, fields

from app.billing.enums import TransactionStatus, TransactionDirection


class Transaction(Model):
    id = fields.BigIntField(pk=True)
    wallet_id = fields.BigIntField()
    status = fields.CharEnumField(enum_type=TransactionStatus)
    direction = fields.CharEnumField(enum_type=TransactionDirection)
    amount = fields.BigIntField()


class Wallet(Model):
    id = fields.BigIntField(pk=True)
    balance = fields.BigIntField(default=0)
    user_id = fields.BigIntField()
