from fastapi import Depends
from app.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional



class DatabaseTransactionService:

    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def delete(self, model_instance):
        await self.db.delete(model_instance)
        await self.db.commit()

    async def create(self, model, relationship: Optional[tuple] = None, **attributes):
        model_instance = model(**attributes)
        if relationship is not None:
            attribute, value = relationship
            setattr(model_instance,attribute,value)
        self.db.add(model_instance)
        await self.db.commit()
        await self.db.refresh(model)
        return model_instance

    async def update(self, model_instance, attribute, value):
        setattr(model_instance,attribute,value)
        await self.db.commit()


