import asyncio
from fastapi import WebSocket
from app.websocket_server.websocket_managers.RedisPubSubManager import (
    RedisPubSubManager,
)
from app.websocket_server.websocket_managers.ServerConnectionManager import (
    ServerConnectionManager,
)
from app.dms.service import DmService
from app.websocket_server.schemas.notification_message import NotificationMessage
from app.file_upload import FileUploadService
from app.servers.service import ServerService
from app.notifications.service import NotificationService
from app.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from app.websocket_server.schemas.websocket_data import (
    WebsocketData,
    websocket_data_adaptor,
)
from app.websocket_server.schemas.websocket_connection import WebsocketConnection
from app.user.service import UserService
from anyio import create_task_group
from typing import Union
import json


class AlwaysTrue:
    def __eq__(self, other):
        return True


class PubSubWebsocketMock:
    def __init__(self, pubsub_client):
        self.pubsub_client: RedisPubSubManager = pubsub_client

    async def send_json(self, data: dict):
        if data["pubsub_publisher"] is None:
            """
                condition to prevent data from being recursively sent
            """
            data["pubsub_publisher"] = self.pubsub_client.id
            await self.pubsub_client._publish(
                channel=settings.PUBSUB_COMMUNICATION_CHANNEL, message=json.dumps(data)
            )

    def append(self):
        pass


class CentralWebsocketServerInterface:
    """
    centralizes all the websocket connections within the whole
    backend across multiple application instances using pubsub
    and WebsocketManager business logic
    """

    def __init__(self):
        self.pubsub_client = RedisPubSubManager(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT
        )
        self.server_manager = ServerConnectionManager()
        self.pub_sub_websocket_mock = PubSubWebsocketMock(
            pubsub_client=self.pubsub_client
        )
        """
            AlwaysTrue() makes it so that all the conditions will
            pass via server_manager broadcast method so the message
            will be sent to the pub sub websocket mock
        """
        self.pub_sub_current_user = WebsocketConnection(
            **{
                "websocket": self.pub_sub_websocket_mock,
                "username": AlwaysTrue(),
                "profile": AlwaysTrue(),
                "dm_ids": [AlwaysTrue()],
                "server_ids": [AlwaysTrue()],
                "user_model": AlwaysTrue(),
            }
        )
        self.server_manager.active_connections.append(self.pub_sub_current_user)

    async def initialize_pubsub(self):
        self.pubsub_client.connect()  # initializes pubsub client
        pubsub_subscriber = await self.pubsub_client.subscribe(
            channel=settings.PUBSUB_COMMUNICATION_CHANNEL
        )
        asyncio.create_task(
            self._pubsub_data_reader(pubsub_subscriber=pubsub_subscriber)
        )

    async def connect(
        self, websocket: WebSocket, current_user: WebsocketConnection, db: AsyncSession
    ):
        await self.server_manager.connect(
            websocket=websocket, current_user=current_user, db=db
        )
        await UserService.set_user_status(status="online", current_user=current_user)

    async def disconnect(self, current_user: WebsocketConnection, db: AsyncSession):
        if not isinstance(current_user.websocket, PubSubWebsocketMock):
            await self.server_manager.disconnect(current_user=current_user, db=db)
            await UserService.set_user_status(
                status="offline", current_user=current_user
            )

    async def broadcast_from_route(self, sender_username: str, message: dict):
        for connection in self.server_manager.active_connections:
            if connection.username == sender_username and not isinstance(
                connection.websocket, PubSubWebsocketMock
            ):
                await self.broadcast(data=message, current_user=connection)

    async def broadcast(
        self, data: Union[dict, WebsocketData], current_user: WebsocketConnection
    ):
        if not isinstance(data, WebsocketData):
            data = websocket_data_adaptor.validate_python(data)
        if data.type in ["file", "textandfile"]:
            await FileUploadService().upload(
                file=data.file, file_type=data.filetype
            )  # modifies data
        await self.server_manager.broadcast(data=data, current_user=current_user)
        async with create_task_group() as task:
            if data.pubsub_publisher is None:
                if data.chat == "dms":
                    task.start_soon(DmService().save_dm_message, data)
                    task.start_soon(
                        self.broadcast,
                        NotificationMessage(
                            **{
                                "dms": data.dm,
                                "sender": data.username,
                                "receiver": data.otheruser,
                                "profile": data.profile,
                            }
                        ),
                        current_user,
                    )
                elif data.chat == "server":
                    task.start_soon(ServerService().save_server_message, data)
                elif data.chat == "notification":
                    if data.type == "message":
                        task.start_soon(
                            NotificationService().save_notification_message, data
                        )

    def add_valid_server_or_dm(self, usernames: list, type: str, id: str):
        self.server_manager.add_valid_server_or_dm(
            usernames=usernames, type=type, id=id
        )

    async def _pubsub_data_reader(self, pubsub_subscriber):
        """
        Reads and broadcasts messages received from Redis PubSub.
        Args:
            pubsub_subscriber (aioredis.ChannelSubscribe): PubSub object for the subscribed channel.
        """
        while True:
            message = await pubsub_subscriber.get_message(
                ignore_subscribe_messages=True
            )
            if message is not None:
                message = json.loads(message["data"].decode())
                """
                    reads websocket messages sent from a different application
                    instance and broadcasts it to the users connected to the 
                    current application instance
                    
                    Note: does not broadcast the websocket message if the instance
                    was the same one that sent the message (its already broadcasted
                    to the websockets connected to that current instance)
                """
                if "pubsub_publisher" in message:
                    if message["pubsub_publisher"] != self.pubsub_client.id:
                        current_user = WebsocketConnection(
                            **{
                                "websocket": self.pub_sub_websocket_mock,
                                "username": message.get("username"),
                                "profile": message.get("profile"),
                                "dm_ids": [AlwaysTrue()],
                                "server_ids": [AlwaysTrue()],
                                "user_model": AlwaysTrue(),
                            }
                        )
                        await self.server_manager.broadcast(
                            data=message, current_user=current_user
                        )


central_ws_interface = CentralWebsocketServerInterface()
