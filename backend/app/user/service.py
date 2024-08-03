from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.user.models import Users
from fastapi import UploadFile
from app.firebase_startup import firebase_storage
from app.auth.service import HashService
from app.file_upload import FileUploadService
from fastapi import Depends
import uuid
import asyncio
from app.base_service import BaseService
from fastapi import HTTPException, status
from typing import Optional


class UserService(BaseService):

    def __init__(self, hash_service: Optional[HashService] = Depends(HashService),
                 file_upload_service: Optional[FileUploadService] = Depends(FileUploadService)):
        super().__init__()
        self.hash_service = hash_service
        self.file_upload_service = file_upload_service

    async def get_user_by_id(self, user_id: int):
        user = await self.transaction.get_by_filters(model=Users,id=user_id)
        return user

    async def create_new_user(self, username: str, email: str, password: str):
        existing_user = await self.transaction.get_by_filters(model=Users, username=username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="User already exists"
            )
        hashed_password = self.hash_service.hash(password)
        new_user = await self.transaction.create(
            model=Users,
            username=username,
            email=email,
            password=hashed_password
        )
        return new_user

    async def upload_profile_picture(self, file: UploadFile):
        file_url = await self.file_upload_service.upload(file=file.file,file_type="jpg")
        return file_url

    async def update_current_profile_picture(
        self, current_user: Users, file: UploadFile
    ):
        file_url = await self.upload_profile_picture(file)
        await self.transaction.update(model_instance=current_user, profile=file_url)
        return file_url

    async def get_ws_user_entities(self, user_id: int) -> Users:
        ws_user_entities = await db.execute(
            select(Users)
            .where(Users.username == username)
            .options(
                selectinload(Users.sent_dms),
                selectinload(Users.received_dms),
                selectinload(Users.server_associations),
            )
        )
        return user_data.scalars().first()

    async def delete_current_user(self, user: Users):
        await self.transaction.delete(user)

    async def set_user_status(self, db: AsyncSession, status: str, current_user: dict):
        current_user["user_model"].status = status
        await db.commit()
