from app.models.notifications import Notifications
from app.models.servers import Server_Messages
from app.models.dms import Dm_Messages
from app.schemas.websocket_data.websocket_data import WebsocketData
from app.schemas.websocket_data.notification_message import NotificationMessage
from app.db.database import SessionLocal
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
import app.ConnectionManagers.ServerConnectionManager as ServerConnectionManager
from app.redis.redis_client import redis_client
from typing import Optional
from app.firebase.firebase_startup import firebase_storage
import uuid
import asyncio
import base64


async def set_user_status(db:AsyncSession,status:str,current_user:dict):
    current_user["user_model"].status = status
    await db.commit()



async def send_notification(data: WebsocketData, current_user: dict):
    notification = NotificationMessage(**{"dm": data.dm,"sender": data.username, "receiver": data.otheruser,"profile": data.profile})
    await ServerConnectionManager.server_manager.broadcast(data=notification, current_user=current_user)

async def save_message(data: WebsocketData, db: Optional[AsyncSession] = None):
    async with SessionLocal(expire_on_commit=False) as db:
        message = None
        if data.chat == "dm":
            message = Dm_Messages.save_dm_message(data.model_dump())
            if data.type == "link":
                await redis_client.set(data.link, data.serverinviteid)
            db.add(message)
        elif data.chat == "server":
            message = Server_Messages.save_server_message(data.model_dump())
            db.add(message)
        elif data.chat == "notification":
            if data.type == "message":
                message = await save_notification(data,db)
        if message is not None:
            await db.commit()
            await db.refresh(message)
        return message

async def save_notification(data: WebsocketData,db: AsyncSession):
    already_received_notification = await db.execute(select(Notifications).where(and_(Notifications.dm == data.dm,
                                                                             Notifications.receiver == data.receiver)))
    already_received_notification = already_received_notification.scalars().first()
    if already_received_notification is not None:
        count = already_received_notification.count + 1
        already_received_notification.count = count
        return already_received_notification
    else:
        count = 1
        data.count = count
        notification = Notifications.save_notification(data.model_dump())
        db.add(notification)
        return notification

async def save_file(data: WebsocketData):
    file_type = data.filetype
    filename = f"{uuid.uuid4()}.{file_type}"
    if "," in data.file:
        file = data.file.split(",")[1]
    else:
        file = data.file
    encoded_file = base64.b64decode(file)
    await asyncio.to_thread(firebase_storage.child(filename).put, encoded_file)
    data.file = f"https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/{filename}?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8"