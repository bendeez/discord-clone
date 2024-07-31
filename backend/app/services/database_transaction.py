from fastapi import Depends
from app.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional


class DatabaseTransactionService:

    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def delete(self, model_instance, ongoing_transaction=False):
        await self.db.delete(model_instance)
        if not ongoing_transaction:
            await self.db.commit()

    async def create(self, model_instance, relationship: Optional[str] = None, relationship_value = None):
        if relationship is not None and relationship_value is not None:
            setattr(model_instance,relationship,relationship_value)
        self.db.add(model_instance)
        await self.db.commit()
        await self.db.refresh(model_instance)
        return model_instance

    async def update(self, model_instance, attribute, value):
        setattr(model_instance, attribute, value)
        await self.db.commit()

    async def execute(self, stmt):
        result = await self.db.execute(stmt)
        return result

    async def scalar(self, stmt):
        result = await self.db.scalar(stmt)
        return result
