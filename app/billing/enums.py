from enum import Enum


class TransactionStatus(Enum):
    registered = 'registered'
    completed = 'completed'
    declined = 'declined'
    error = 'error'


class TransactionDirection(Enum):
    credit = 'credit'
    debit = 'debit'
