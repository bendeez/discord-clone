from fastapi import WebSocket
from RedisPubSubManager import RedisPubSubManager
from ServerConnectionManager import ServerConnectionManager
from app.core.config import Settings
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.websocket_data.websocket_data import WebsocketData
from typing import Union
import json


class PubSubWebsocketMock:

    def __init__(self, pubsub_client):
        self.pubsub_client: RedisPubSubManager = pubsub_client

    async def send_json(self, data: dict):
        if "pub_sub" in data:
            if data["pub_sub"]:
                """
                    condition to prevent data from being recursively sent
                """
                data["pub_sub"] = True
                await self.pubsub_client._publish(channel=Settings.PUBSUB_COMMUNICATION_CHANNEL,
                                                  message=json.dumps(data))

    @classmethod
    def current_user(cls, pubsub_client: RedisPubSubManager):
        return {"websocket":cls(pubsub_client=pubsub_client),
                "server_ids":[],"dm_ids":[], "username":""}



class CentralWebsocketServerInterface:
    """
        centralizes all the websocket connections within the whole
        backend across multiple application instances using pubsub
        and WebsocketManager business logic
    """
    def __init__(self):
        self.pubsub_client = RedisPubSubManager(host=Settings.REDIS_HOST, port=Settings.REDIS_PORT)
        self.pubsub_client.subscribe(channel=Settings.PUBSUB_COMMUNICATION_CHANNEL)
        self.server_manager = ServerConnectionManager()
        pub_sub_current_user = PubSubWebsocketMock.current_user(pubsub_client=self.pubsub_client)
        self.server_manager.active_connections.append(pub_sub_current_user)

    async def connect(self, websocket: WebSocket, current_user: dict, db: AsyncSession):
        await self.server_manager.connect(websocket=websocket, current_user=current_user, db=db)

    async def disconnect(self, current_user: dict,db: AsyncSession):
        await self.server_manager.disconnect(current_user=current_user, db=db)

    async def broadcast_from_route(self, sender_username: str, message: dict):
        await self.server_manager.broadcast_from_route(sender_username=sender_username, message=message)

    async def broadcast(self, data: Union[dict,WebsocketData], current_user: dict):
        for connection in self.server_manager.active_connections:
            if isinstance(connection["websocket"],PubSubWebsocketMock):
                connection.update({"dm_ids":current_user["dm_ids"],"server_ids":current_user["server_ids"],
                                   "username":current_user["username"]})
        await self.server_manager.broadcast(data=data, current_user=current_user)

    def add_valid_server_or_dm(self, usernames: list, type: str, id: str):
        self.server_manager.add_valid_server_or_dm(usernames=usernames, type=type, id=id)


