from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from fastapi import Depends
from db.database import get_db
from app.user.models import Users


class DatabaseTransactionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def delete(self, model_instance, ongoing_transaction=False):
        await self.db.delete(model_instance)
        if not ongoing_transaction:
            await self.db.commit()

    async def create(
        self,
        model_instance
    ):
        self.db.add(model_instance)
        await self.db.commit()
        await self.db.refresh(model_instance)
        return model_instance

    async def update(self, model_instance, attribute, value):
        setattr(model_instance, attribute, value)
        await self.db.commit()

    async def get_by_user_ids(self, model, current_user: Users, remote_id: int):
        stmt = select(model).where(
                        or_(
                            and_(
                                model.sender == current_user.id,
                                model.receiver == remote_id,
                            ),
                            and_(
                                model.receiver == current_user.id,
                                model.sender == remote_id,
                            ),
                        )
                    )
        model_instance = await self.db.execute(stmt)
        return model_instance.scalars().first()

    async def check_user_in_entity(self, model, current_user: Users, entity_id) -> bool:
        stmt = select(
            or_(model.sender == current_user, model.receiver == current_user)
        ).where(model.id == entity_id)
        user_in_dm = await self.db.scalar(stmt)
        return user_in_dm or False

    @classmethod
    def get_instance(cls, db: AsyncSession = Depends(get_db)):
        """
        for dependency injection
        """
        return cls(db=db)
