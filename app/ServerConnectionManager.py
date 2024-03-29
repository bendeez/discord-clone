from fastapi import WebSocket
from typing import Union
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import models
import redis

redis_client = redis.Redis(host="redis",port=6379,db=0,decode_responses=True)

async def send_notification(websocket:WebSocket,data:dict,current_user:dict,db:AsyncSession):
    dm = data["dm"]
    username = data["username"]
    other_user = data["otheruser"]
    profile = data["profile"]
    notification = {"chat": "notification", "type": "message","dm":dm,"sender":username,"receiver":other_user,"profile":profile}
    await server_manager.broadcast(websocket, notification, current_user,db)


async def save_message(data: dict, db: AsyncSession):
    chat = data.get("chat")
    type = data.get("type")
    username = data.get("username")
    if chat == "dm":
        dm = data["dm"]
        if type == "text":
            text = data["text"]
            message = models.Dm_Messages(text=text, username=username, dm=dm, created_date=datetime.now())
            db.add(message)
        if type == "file":
            file = data["file"]
            file_type = data["filetype"]
            message = models.Dm_Messages(file=file, filetype=file_type, username=username, dm=dm,
                                         created_date=datetime.now())
            db.add(message)
        if type == "textandfile":
            text = data["text"]
            file = data["file"]
            file_type = data["filetype"]
            message = models.Dm_Messages(text=text, file=file, filetype=file_type, username=username, dm=dm,
                                         created_date=datetime.now())
            db.add(message)
        if type == "link":
            link = data["link"]
            server_invite_id = data["serverinviteid"]
            message = models.Dm_Messages(link=link, username=username, dm=dm, serverinviteid=server_invite_id,
                                         created_date=datetime.now())
            db.add(message)
            redis_client.set(link, server_invite_id)
    if chat == "server":
        server = data["server"]
        if type == "text":
            text = data["text"]
            message = models.Server_Messages(text=text, username=username, server=server,
                                             created_date=datetime.now())
            db.add(message)
        if type == "file":
            file = data["file"]
            file_type = data["filetype"]
            message = models.Server_Messages(file=file, filetype=file_type, username=username, server=server,
                                             created_date=datetime.now())
            db.add(message)
        if type == "textandfile":
            text = data["text"]
            file = data["file"]
            file_type = data["filetype"]
            message = models.Server_Messages(text=text, file=file, filetype=file_type, username=username,
                                             server=server, created_date=datetime.now())
            db.add(message)
        if type == "announcement":
            username = data["username"]
            announcement = data["announcement"]
            server = data["server"]
            message = models.Server_Messages(announcement=announcement, username=username, server=server,
                                             created_date=datetime.now())
            db.add(message)
    if chat == "notification":
        dm = data["dm"]
        sender = data["sender"]
        receiver = data["receiver"]
        already_notification = await db.execute(select(models.Notifications).filter(models.Notifications.dm == dm))
        already_notification = already_notification.scalars().first()
        if already_notification:
            count = already_notification.count + 1
            already_notification.count = count
        else:
            count = 1
            save_notification = models.Notifications(sender=sender, receiver=receiver, dm=dm, count=count)
            db.add(save_notification)
    await db.commit()
class ServerConnectionManager:
    def __init__(self):
        self.active_connections: list[dict[str,Union[list[int],str,WebSocket]]] = []
    async def connect(self,websocket:WebSocket,current_user:dict):
        await websocket.accept()
        self.active_connections.append(current_user)
    def disconnect(self,websocket:WebSocket,current_user:dict):
        self.active_connections.remove(current_user)
    async def broadcast(self,websocket:WebSocket,data:dict,current_user:dict,db:AsyncSession):
        try:
            chat = data.get("chat")
            if chat == "dm":
                dm = data.get("dm")
                if dm in current_user.get("dm_ids",[]):
                    for connection in self.active_connections:
                        if dm in connection.get("dm_ids",[]):
                            await connection.get("websocket").send_json(data)
                    await save_message(data,db)
                    await send_notification(websocket,data,current_user,db)
            elif chat == "server":
                server = data.get("server")
                if server in current_user.get("server_ids",[]):
                    for connection in self.active_connections:
                        if server in connection.get("server_ids",[]):
                            await connection.get("websocket").send_json(data)
                    await save_message(data, db)
            elif chat == "notification":
                for connection in self.active_connections:
                    if data.get("receiver") == connection.get("username"):
                        await connection.get("websocket").send_json(data)
                await save_message(data, db)
            elif chat == "notificationall":
                for connection in self.active_connections:
                    await connection.get("websocket").send_json(data)
                await save_message(data, db)
        except Exception as e:
            print(e)
    def add_valid_server_or_dm(self,usernames:list,type,id):
        for connection in self.active_connections:
            if connection.get("username") in usernames:
                if isinstance(connection.get(type),list):
                    connection.get(type).append(int(id))

server_manager = ServerConnectionManager()