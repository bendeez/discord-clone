from database_transaction import DatabaseTransactionService
from fastapi import Depends
from app.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:
    def __init__(self, db: AsyncSession =Depends(get_db)):
        self.transaction = DatabaseTransactionService(db=db)


