from app.database_transaction import DatabaseTransactionService
from fastapi import Depends

class BaseService:

    def __init__(self, transaction: DatabaseTransactionService = Depends(DatabaseTransactionService)):
        self.transaction: DatabaseTransactionService = transaction



