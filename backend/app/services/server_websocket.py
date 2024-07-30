from app.models.notifications import Notifications
from app.models.servers import Server_Messages
from app.models.dms import Dm_Messages
from app.schemas.websocket_data.websocket_data import WebsocketData
from app.schemas.websocket_data.notification_message import Notification
from app.db.database import SessionLocal
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
import app.WebsocketManagers.CentralWebsocketServerInterface as CentralWebsocketServerInterface
from app.redis_client import redis_client
from file_upload import FileUploadService
from base import BaseService

"""
    condition: if data.pubsub_publisher is None
    prevents an action from being performed twice 
    across multiple app instances to avoid duplicate
    data
"""

class ServerWebsocketService(BaseService):

    async def send_notification(self, notification: Notification, current_user: dict):
        if data.pubsub_publisher is None:
            await CentralWebsocketServerInterface.central_ws_interface.broadcast(data=notification, current_user=current_user)


    async def save_message(self, data: WebsocketData):
        if data.pubsub_publisher is None:
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
                        message = await self.save_notification(data,db)
                if message is not None:
                    await db.commit()
                    await db.refresh(message)
                return message

    async def save_notification(self, data: WebsocketData,db: AsyncSession):
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

    async def save_file(self, data: WebsocketData):
        if data.pubsub_publisher is None:
            file_url = await FileUploadService.upload(file=data.file,file_type=data.filetype)
            data.file = file_url

