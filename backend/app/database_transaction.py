from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, tuple_
from sqlalchemy.orm import selectinload
from fastapi import Depends
from app.database import get_db
from base_models import SelfRelationship


class DatabaseTransactionService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    def execute(self, method):
        async def wrapper(*args, **kwargs):
            stmt = method(*args, **kwargs)
            model_instance = await self.db.execute(stmt)
            return model_instance.scalars().first()

        return wrapper
    def load_relationships(self, method):

        def wrapper(*args, **kwargs):
            stmt = method(*args,**kwargs)
            relationships = kwargs["relationships"]
            load_options = [selectinload(getattr(model, attribute)) for model, attribute in relationships.items()]
            stmt = stmt.options(*load_options)
            return stmt

        return wrapper
    async def delete(self, model_instance, ongoing_transaction=False):
        await self.db.delete(model_instance)
        if not ongoing_transaction:
            await self.db.commit()

    async def create(
        self,
        model,
        relationship: dict = {},
        **attributes
    ):
        if isinstance(model, SelfRelationship):
            model_instance = model.check_and_create(**attributes)
        else:
            model_instance = model(**attributes)
        for key, value in relationship.items():
            model_instance.key = value
        self.db.add(model_instance)
        await self.db.commit()
        await self.db.refresh(model_instance)
        return model_instance

    async def update(self, model_instance, **attributes):
        for attribute, value in attributes.items():
            setattr(model_instance, attribute, value)
        await self.db.commit()

    @execute
    @load_relationships
    def get_by_user_ids(self, model, current_user_id: int, remote_id: int, relationships: dict = {}):
        stmt = select(model).where(tuple_(model.sender_id, model.receiver_id)
               .in_([(current_user_id, remote_id),(remote_id, current_user_id)]))
        return stmt

    @execute
    @load_relationships
    def get_by_filters(self, model, relationships: dict = {}, **filters):
        conditions = [getattr(model, attribute) == value for attribute, value in filters.items()]
        stmt = select(model).where(and_(*conditions))
        return stmt

    async def check_user_in_entity(self, model, current_user_id: int, entity_id: int) -> bool:
        stmt = select(
            or_(model.sender_id == current_user_id, model.receiver_id == current_user_id)
        ).where(model.id == entity_id)
        user_in_entity = await self.db.scalar(stmt)
        return user_in_entity or False

