from fastapi import WebSocket
from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.server_websocket import save_message, send_notification
from app.crud.server_websocket import set_user_status
from app.schemas.websocket_data.websocket_data import WebsocketData,websocket_data_adaptor
from app.schemas.websocket_data.notificationall_message import NotificationAllStatus
from datetime import datetime
from app.firebase.firebase_startup import firebase_storage
import uuid
import asyncio
from anyio import create_task_group
from uuid import uuid4
import base64


class ServerConnectionManager:
    def __init__(self):
        self.active_connections: list[dict[str, Union[list[int], str, WebSocket]]] = []

    async def connect(self, websocket: WebSocket, current_user: dict,db: AsyncSession):
        await websocket.accept()
        self.active_connections.append(current_user)
        await set_user_status(db=db, status="online", current_user=current_user)
        await self.broadcast(data=NotificationAllStatus(**{"status": "online", "username": current_user["username"]}),
                             current_user=current_user)

    async def broadcast_from_route(self, sender_username: str, message: dict):
        for connection in self.active_connections:
            if connection["username"] == sender_username:
                await server_manager.broadcast(data=message,
                                               current_user=connection)
                return # avoid broadcasting twice if multiple users (different devices) have same username

    async def disconnect(self, current_user: dict,db: AsyncSession):
        self.active_connections.remove(current_user)
        await set_user_status(db=db, status="offline", current_user=current_user)
        await self.broadcast(data=NotificationAllStatus(**{"status": "offline","username": current_user["username"]}),
                             current_user=current_user)

    async def broadcast(self, data: Union[dict,WebsocketData], current_user: dict):
        data = websocket_data_adaptor.validate_python(data)
        try:
            chat = data.chat
            if chat == "dm": # checks if the message is being sent to a dm
                await self.broadcast_dm(data=data,current_user=current_user)
            elif chat == "server":
                await self.broadcast_server(data=data,current_user=current_user)
            elif chat == "notification":
                await self.broadcast_notification(data=data,current_user=current_user)
            elif chat == "notificationall":
                await self.broadcast_notification_all(data=data,current_user=current_user)
        except Exception as e:
            print(e)

    async def save_file(self, data: WebsocketData):
        file_type = data.filetype
        filename = f"{uuid.uuid4()}.{file_type}"
        if "," in data.file:
            file = data.file.split(",")[1]
        else:
            file = data.file
        encoded_file = base64.b64decode(file)
        await asyncio.to_thread(firebase_storage.child(filename).put, encoded_file)
        data.file = f"https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/{filename}?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8"

    def update_dm_message(self, data: WebsocketData, current_user: dict):
        data.username = current_user["username"]
        data.profile = current_user["profile"]
        data.date = datetime.now()

    async def broadcast_dm(self, data: WebsocketData, current_user: dict):
        if data.dm in current_user["dm_ids"]:  # checks if the dm id is a part of the user's dms
            if data.type == "file" or data.type == "textandfile":
                await self.save_file(data)
            if data.type == "link":
                data.link = str(uuid4())
            self.update_dm_message(data=data, current_user=current_user)
            data_dict = data.model_dump()
            data_dict["date"] = str(data_dict["date"])
            async with create_task_group() as task:
                for connection in self.active_connections:  # loops through all connections
                    if data.dm in connection["dm_ids"]:  # checks if the dm id is a part of the remote user's dms
                        task.start_soon(connection["websocket"].send_json,data_dict) # sends a message if it is
                task.start_soon(save_message,data)
                task.start_soon(send_notification,data,current_user)

    def update_server_message(self, data: WebsocketData, current_user: dict):
        data.username = current_user["username"]
        data.profile = current_user["profile"]
        data.date = datetime.now()

    async def broadcast_server(self, data: WebsocketData, current_user: dict):
        if data.server in current_user["server_ids"]:
            if data.type == "file" or data.type == "textandfile":
                await self.save_file(data)
            self.update_server_message(data=data, current_user=current_user)
            data_dict = data.model_dump()
            data_dict["date"] = str(data_dict["date"])
            async with create_task_group() as task:
                for connection in self.active_connections:
                    if data.server in connection["server_ids"]:
                        task.start_soon(connection["websocket"].send_json,data_dict)
                task.start_soon(save_message,data)

    def update_notification(self, data: WebsocketData, current_user: dict):
        data.sender = current_user["username"]
        data.profile = current_user["profile"]

    async def broadcast_notification(self, data: WebsocketData, current_user: dict):
        self.update_notification(data=data,current_user=current_user)
        async with create_task_group() as task:
            for connection in self.active_connections:
                if data.receiver == connection["username"]:
                    task.start_soon(connection["websocket"].send_json,data.model_dump())
            task.start_soon(save_message,data)

    def update_notification_all(self, data: WebsocketData, current_user: dict):
        data.username = current_user["username"]

    async def broadcast_notification_all(self, data: WebsocketData, current_user: dict):
        self.update_notification_all(data=data, current_user=current_user)
        async with create_task_group() as task:
            for connection in self.active_connections:
                task.start_soon(connection["websocket"].send_json,data.model_dump())
            task.start_soon(save_message,data)


    def add_valid_server_or_dm(self, usernames: list, type: str, id: str):
        for connection in self.active_connections:
            if connection["username"] in usernames:
                if isinstance(connection.get(type), list):
                    connection.get(type).append(int(id))


server_manager = ServerConnectionManager()
