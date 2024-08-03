from fastapi import WebSocket
from typing import Union
from app.websocket_server.schemas.websocket_data import (
    WebsocketData,
    websocket_data_adaptor,
)
from app.websocket_server.schemas.websocket_connection import WebsocketConnection
from app.websocket_server.schemas.notificationall_message import NotificationAllStatus
from datetime import datetime
from anyio import create_task_group


class ServerConnectionManager:
    def __init__(self):
        self.active_connections: list[WebsocketConnection] = []

    async def connect(self, websocket: WebSocket, current_user: WebsocketConnection):
        await websocket.accept()
        self.active_connections.append(current_user)
        await self.broadcast(
            data=NotificationAllStatus(
                **{"status": "online", "username": current_user["username"]}
            ),
            current_user=current_user,
        )

    async def disconnect(self, current_user: WebsocketConnection):
        self.active_connections.remove(current_user)
        await self.broadcast(
            data=NotificationAllStatus(
                **{"status": "offline", "username": current_user["username"]}
            ),
            current_user=current_user,
        )

    async def broadcast(
        self, data: Union[dict, WebsocketData], current_user: WebsocketConnection
    ):
        if not isinstance(data, WebsocketData):
            data = websocket_data_adaptor.validate_python(data)
        chat = data.chat
        if chat == "dm":  # checks if the message is being sent to a dm
            await self.broadcast_dm(data=data, current_user=current_user)
        elif chat == "server":
            await self.broadcast_server(data=data, current_user=current_user)
        elif chat == "notification":
            await self.broadcast_notification(data=data, current_user=current_user)
        elif chat == "notificationall":
            await self.broadcast_notification_all(data=data, current_user=current_user)

    async def broadcast_dm(
        self, data: WebsocketData, current_user: WebsocketConnection
    ):
        if (
            data.dm in current_user["dm_ids"]
        ):  # checks if the dm id is a part of the user's dm
            """
                fills in attributes that the server is suppose to set
            """
            data = websocket_data_adaptor.validate_python(
                dict(
                    **data.model_dump(exclude={"username", "profile", "date"}),
                    username=current_user["username"],
                    profile=current_user["profile"],
                    date=datetime.now(),
                )
            )
            try:
                async with create_task_group() as task:
                    for connection in self.active_connections:
                        if data.dm in connection.dm_ids:
                            task.start_soon(
                                connection.websocket.send_json,
                                data.make_json_compatible(),
                            )
            except* Exception as excgroup:
                for e in excgroup.exceptions:
                    print(e)

    async def broadcast_server(
        self, data: WebsocketData, current_user: WebsocketConnection
    ):
        if data.server in current_user["server_ids"]:
            data = websocket_data_adaptor.validate_python(
                dict(
                    **data.model_dump(exclude={"username", "profile", "date"}),
                    username=current_user["username"],
                    profile=current_user["profile"],
                    date=datetime.now(),
                )
            )
            try:
                async with create_task_group() as task:
                    for connection in self.active_connections:
                        if data.server in connection.server_ids:
                            task.start_soon(
                                connection.websocket.send_json,
                                data.make_json_compatible(),
                            )
            except* Exception as excgroup:
                for e in excgroup.exceptions:
                    print(e)

    async def broadcast_notification(
        self, data: WebsocketData, current_user: WebsocketConnection
    ):
        data = websocket_data_adaptor.validate_python(
            dict(
                **data.model_dump(exclude={"sender", "profile"}),
                sender=current_user.username,
                profile=current_user.profile,
            )
        )
        try:
            async with create_task_group() as task:
                for connection in self.active_connections:
                    if data.receiver == connection.username:
                        task.start_soon(
                            connection.websocket.send_json, data.model_dump()
                        )
        except* Exception as excgroup:
            for e in excgroup.exceptions:
                print(e)

    async def broadcast_notification_all(
        self, data: WebsocketData, current_user: WebsocketConnection
    ):
        data = websocket_data_adaptor.validate_python(
            dict(
                **data.model_dump(exclude={"username"}),
                username=current_user.username,
            )
        )
        try:
            async with create_task_group() as task:
                for connection in self.active_connections:
                    task.start_soon(connection.websocket.send_json, data.model_dump())
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
            if connection.username in usernames:
                connection_type = getattr(connection, type)
                connection_type.append(int(id))
