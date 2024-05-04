from datetime import datetime
from fastapi import WebSocket
from app.models.notifications import Notifications
from app.models.servers import Server_Messages
from app.models.dms import Dm_Messages
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import app.routers.server_websocket.ServerConnectionManager as ServerConnectionManager
import redis

redis_client = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

async def set_user_status(db:AsyncSession,status:str,current_user:dict):
    current_user["user_model"].status = status
    await db.commit()

async def save_notification(db:AsyncSession,data:dict):
    dm = data["dm"]
    sender = data["sender"]
    receiver = data["receiver"]
    already_notification = await db.execute(select(Notifications).filter(Notifications.dm == dm))
    already_notification = already_notification.scalars().first()
    if already_notification:
        count = already_notification.count + 1
        already_notification.count = count
    else:
        count = 1
        save_notification = Notifications(sender=sender, receiver=receiver, dm=dm, count=count)
        db.add(save_notification)
    await db.commit()

async def send_notification(websocket: WebSocket, data: dict, current_user: dict, db: AsyncSession):
    dm = data["dm"]
    username = data["username"]
    other_user = data["otheruser"]
    profile = data["profile"]
    notification = {"chat": "notification", "type": "message", "dm": dm, "sender": username, "receiver": other_user,
                    "profile": profile}
    await ServerConnectionManager.server_manager.broadcast(websocket, notification, current_user,db)
    await save_notification(db=db,data=notification)

async def save_message(data: dict, db: AsyncSession):
    chat = data.get("chat")
    type = data.get("type")
    username = data.get("username")
    if chat == "dm":
        dm = data["dm"]
        if type == "text":
            text = data["text"]
            message = Dm_Messages(text=text, username=username, dm=dm, created_date=datetime.now())
            db.add(message)
        if type == "file":
            file = data["file"]
            file_type = data["filetype"]
            message = Dm_Messages(file=file, filetype=file_type, username=username, dm=dm,
                                  created_date=datetime.now())
            db.add(message)
        if type == "textandfile":
            text = data["text"]
            file = data["file"]
            file_type = data["filetype"]
            message = Dm_Messages(text=text, file=file, filetype=file_type, username=username, dm=dm,
                                  created_date=datetime.now())
            db.add(message)
        if type == "link":
            link = data["link"]
            server_invite_id = data["serverinviteid"]
            message = Dm_Messages(link=link, username=username, dm=dm, serverinviteid=server_invite_id,
                                  created_date=datetime.now())
            db.add(message)
            redis_client.set(link, server_invite_id)
    if chat == "server":
        server = data["server"]
        if type == "text":
            text = data["text"]
            message = Server_Messages(text=text, username=username, server=server,
                                      created_date=datetime.now())
            db.add(message)
        if type == "file":
            file = data["file"]
            file_type = data["filetype"]
            message = Server_Messages(file=file, filetype=file_type, username=username, server=server,
                                      created_date=datetime.now())
            db.add(message)
        if type == "textandfile":
            text = data["text"]
            file = data["file"]
            file_type = data["filetype"]
            message = Server_Messages(text=text, file=file, filetype=file_type, username=username,
                                      server=server, created_date=datetime.now())
            db.add(message)
        if type == "announcement":
            username = data["username"]
            announcement = data["announcement"]
            server = data["server"]
            message = Server_Messages(announcement=announcement, username=username, server=server,
                                      created_date=datetime.now())
            db.add(message)
    await db.commit()