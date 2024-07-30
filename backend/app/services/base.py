from database_transaction import DatabaseTransactionService
from typing import Optional


class BaseService:
    def __init__(self, transaction: Optional[DatabaseTransactionService] = None):
        if transaction is None:
            transaction = DatabaseTransactionService()
        self.transaction = transaction

    @classmethod
    def get_instance(cls):
        return cls()
