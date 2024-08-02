from app.database_transaction import DatabaseTransactionService
from fastapi import Depends


class BaseService:
    def __init__(self, transaction: DatabaseTransactionService):
        self.transaction: DatabaseTransactionService = transaction

    @classmethod
    def get_instance(
        cls,
        transaction_service: DatabaseTransactionService = Depends(
            DatabaseTransactionService.get_instance
        ),
    ):
        """
        for dependency injection
        """
        return cls(transaction=transaction_service)
