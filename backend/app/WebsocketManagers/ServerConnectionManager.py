from fastapi import WebSocket
from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.server_websocket import save_message, send_notification, set_user_status, save_file
from app.schemas.websocket_data.websocket_data import WebsocketData,websocket_data_adaptor
from app.schemas.websocket_data.notificationall_message import NotificationAllStatus
from datetime import datetime
from anyio import create_task_group
from uuid import uuid4


class ServerConnectionManager:
    def __init__(self):
        self.active_connections: list[dict[str, Union[list[int], str, WebSocket]]] = []

    async def connect(self, websocket: WebSocket, current_user: dict, db: AsyncSession):
        await websocket.accept()
        self.active_connections.append(current_user)
        await set_user_status(db=db, status="online", current_user=current_user)
        await self.broadcast(data=NotificationAllStatus(**{"status": "online", "username": current_user["username"]}),
                             current_user=current_user)

    async def disconnect(self, current_user: dict,db: AsyncSession):
        self.active_connections.remove(current_user)
        await set_user_status(db=db, status="offline", current_user=current_user)
        await self.broadcast(data=NotificationAllStatus(**{"status": "offline","username": current_user["username"]}),
                             current_user=current_user)

    async def broadcast(self, data: Union[dict, WebsocketData], current_user: dict):
        data = websocket_data_adaptor.validate_python(data)
        chat = data.chat
        if chat == "dm": # checks if the message is being sent to a dm
            await self.broadcast_dm(data=data,current_user=current_user)
        elif chat == "server":
            await self.broadcast_server(data=data,current_user=current_user)
        elif chat == "notification":
            await self.broadcast_notification(data=data,current_user=current_user)
        elif chat == "notificationall":
            await self.broadcast_notification_all(data=data,current_user=current_user)

    async def broadcast_dm(self, data: WebsocketData, current_user: dict):
        if data.dm in current_user["dm_ids"]:  # checks if the dm id is a part of the user's dms
            if data.type in ["file","textandfile"]:
                await save_file(data)
            if data.type == "link":
                data.link = str(uuid4())
            """
                fills in attributes that the server is suppose to set
            """
            data = websocket_data_adaptor.validate_python(dict(**data.model_dump(exclude={"username","profile","date"}),
                                                          username=current_user["username"],
                                                          profile=current_user["profile"],
                                                          date=datetime.now()))
            try:
                async with create_task_group() as task:
                    for connection in self.active_connections:  # loops through all connections
                        if data.dm in connection["dm_ids"]:  # checks if the dm id is a part of the remote user's dms
                            task.start_soon(connection["websocket"].send_json,data.make_json_compatible()) # sends a message if it is
                    task.start_soon(save_message,data)
                    task.start_soon(send_notification,data,current_user)
            except *Exception as excgroup:
                for e in excgroup.exceptions:
                    print(e)


    async def broadcast_server(self, data: WebsocketData, current_user: dict):
        if data.server in current_user["server_ids"]:
            if data.type in ["file","textandfile"]:
                await save_file(data)
            data = websocket_data_adaptor.validate_python(dict(**data.model_dump(exclude={"username", "profile", "date"}),
                                                         username=current_user["username"],
                                                         profile=current_user["profile"],
                                                         date=datetime.now()))
            try:
                async with create_task_group() as task:
                    for connection in self.active_connections:
                        if data.server in connection["server_ids"]:
                            task.start_soon(connection["websocket"].send_json,data.make_json_compatible())
                    task.start_soon(save_message,data)
            except* Exception as excgroup:
                for e in excgroup.exceptions:
                    print(e)


    async def broadcast_notification(self, data: WebsocketData, current_user: dict):
        data = websocket_data_adaptor.validate_python(dict(**data.model_dump(exclude={"sender", "profile"}),
                                                           sender=current_user["username"],
                                                           profile=current_user["profile"]))
        try:
            async with create_task_group() as task:
                for connection in self.active_connections:
                    if data.receiver == connection["username"]:
                        task.start_soon(connection["websocket"].send_json,data.model_dump())
                task.start_soon(save_message,data)
        except* Exception as excgroup:
            for e in excgroup.exceptions:
                print(e)

    async def broadcast_notification_all(self, data: WebsocketData, current_user: dict):
        data = websocket_data_adaptor.validate_python(dict(**data.model_dump(exclude={"username"}),
                                                           username=current_user["username"]))
        try:
            async with create_task_group() as task:
                for connection in self.active_connections:
                    task.start_soon(connection["websocket"].send_json,data.model_dump())
                task.start_soon(save_message,data)
        except* Exception as excgroup:
            for e in excgroup.exceptions:
                print(e)


    def add_valid_server_or_dm(self, usernames: list, type: str, id: str):
        """
            adds the authorized dm or server ids to the current_user dict
            so the user has access to the entity when a user has recently
            (same websocket connection before and after the creation)
            created or joined a dm or server
        """
        for connection in self.active_connections:
            if connection["username"] in usernames:
                connection[type].append(int(id))

