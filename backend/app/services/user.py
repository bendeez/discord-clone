from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.user import Users
from fastapi import UploadFile
from app.firebase_startup import firebase_storage
from app.utils import hash
import uuid
import asyncio
from base import BaseService

class UserService(BaseService):

    async def check_user_exists(self, db: AsyncSession, remote_user_username: str):
        user = await get_user(db=db,remote_user_username=remote_user_username)
        if user is not None:
            return True
        return False

    async def get_user(self, db: AsyncSession, remote_user_username: str):
        user_exists = await db.execute(select(Users).where(Users.username == remote_user_username))
        return user_exists.scalars().first()

    async def create_new_user(self, username: str, email: str, password: str):
        hashed_password = hash(password)
        new_user = await self.transaction.create(model_instance=Users(username=username, email=email, password=hashed_password))
        return new_user


    async def upload_profile_picture(self, file: UploadFile):
        file_type = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{file_type}"
        await asyncio.to_thread(firebase_storage.child(filename).put, file.file.read())
        return filename

    async def update_current_profile_picture(self, db: AsyncSession, current_user: Users, file: UploadFile):
        filename = await self.upload_profile_picture(file)
        current_user.profile = f"https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/{filename}?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8"
        await db.commit()
        return {"profile": f"https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/{filename}?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8"}


    async def get_user_data(self, db: AsyncSession, username) -> Users:
        user_data = await db.execute(select(Users)
                                     .where(Users.username == username)
                                     .options(selectinload(Users.sent_dms), selectinload(Users.received_dms),
                                              selectinload(Users.server_associations)))
        return user_data.scalars().first()

    async def delete_current_user(self, user: Users):
        await self.transaction.delete(user)

    async def set_user_status(self, db:AsyncSession,status:str,current_user:dict):
        current_user["user_model"].status = status
        await db.commit()