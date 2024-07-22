import asyncio
from fastapi import WebSocket
from RedisPubSubManager import RedisPubSubManager
from ServerConnectionManager import ServerConnectionManager
from app.core.config import Settings
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.websocket_data.websocket_data import WebsocketData
from typing import Union
import json


class AlwaysTrue:
    def __eq__(self, other):
        return True

class PubSubWebsocketMock:

    def __init__(self, pubsub_client):
        self.pubsub_client: RedisPubSubManager = pubsub_client

    async def send_json(self, data: dict):
        if "pubsub_publisher" not in data:
            """
                condition to prevent data from being recursively sent
            """
            data["pubsub_publisher"] = self.pubsub_client.id
            await self.pubsub_client._publish(channel=Settings.PUBSUB_COMMUNICATION_CHANNEL,
                                              message=json.dumps(data))

    @classmethod
    def current_user(cls, pubsub_client: RedisPubSubManager):
        """
            AlwaysTrue() makes it so that all the conditions will
            pass via server_manager broadcast method so the message
            will be sent to the pub sub websocket mock
        :param pubsub_client:
        :return:
        """
        return {"websocket":PubSubWebsocketMock(pubsub_client=pubsub_client),
                "dm_ids":AlwaysTrue(),"server_ids":AlwaysTrue(),
                "username":AlwaysTrue()}



class CentralWebsocketServerInterface:
    """
        centralizes all the websocket connections within the whole
        backend across multiple application instances using pubsub
        and WebsocketManager business logic
    """
    def __init__(self):
        self.pubsub_client = RedisPubSubManager(host=Settings.REDIS_HOST, port=Settings.REDIS_PORT)
        pubsub_subscriber = await self.pubsub_client.subscribe(channel=Settings.PUBSUB_COMMUNICATION_CHANNEL)
        asyncio.create_task(self._pubsub_data_reader(pubsub_subscriber=pubsub_subscriber))
        self.server_manager = ServerConnectionManager()
        self.pub_sub_current_user = PubSubWebsocketMock.current_user(pubsub_client=self.pubsub_client)
        self.server_manager.active_connections.append(self.pub_sub_current_user)

    async def connect(self, websocket: WebSocket, current_user: dict, db: AsyncSession):
        await self.server_manager.connect(websocket=websocket, current_user=current_user, db=db)

    async def disconnect(self, current_user: dict,db: AsyncSession):
        await self.server_manager.disconnect(current_user=current_user, db=db)

    async def broadcast_from_route(self, sender_username: str, message: dict):
        await self.server_manager.broadcast_from_route(sender_username=sender_username, message=message)

    async def broadcast(self, data: Union[dict,WebsocketData], current_user: dict):
        await self.server_manager.broadcast(data=data, current_user=current_user)

    def add_valid_server_or_dm(self, usernames: list, type: str, id: str):
        self.server_manager.add_valid_server_or_dm(usernames=usernames, type=type, id=id)

    async def _pubsub_data_reader(self, pubsub_subscriber):
        """
        Reads and broadcasts messages received from Redis PubSub.

        Args:
            pubsub_subscriber (aioredis.ChannelSubscribe): PubSub object for the subscribed channel.
        """
        while True:
            message = await pubsub_subscriber.get_message(ignore_subscribe_messages=True)
            if message is not None:
                if message["pubsub_publisher"] != self.pubsub_client.id:
                    message = json.loads(message.decode())
                    await self.server_manager.broadcast(data=message,current_user=self.pub_sub_current_user)

central_ws_interface = CentralWebsocketServerInterface()