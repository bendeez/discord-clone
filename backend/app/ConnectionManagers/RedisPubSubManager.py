import redis.asyncio as aioredis
import asyncio
from typing import Optional
import json

class RedisPubSubManager:
    def __init__(self, host, port, global_redis_client):
        self.host = host
        self.port = port
        self.global_redis_client: aioredis.Redis = global_redis_client
        self.redis_connection: Optional[aioredis.Redis] = None
        self.pubsub: Optional[aioredis.Redis.pubsub] = None

    def connect(self):
        self.redis_connection = aioredis.Redis(host=self.host, port=self.port,
                                               db=0, decode_responses=True)
        self.pubsub = self.redis_connection.pubsub()

    async def publish(self, channel, data):
        await self.redis_connection.publish(channel, data)

    async def subscribe(self, channels: dict):
        await self.subscribe_to_channels(channels=channels)
        await self.add_channels_to_cache(channels=channels)
        asyncio.create_task(self.wait_for_message())

    async def subscribe_to_channels(self, channels: dict):
        tasks = []
        for type, channels_by_type in channels.items():
            if isinstance(channels_by_type, list):
                for channel in channels_by_type:
                    tasks.append(self.pubsub.subscribe(f"{type}-{channel}"))
            else:
                tasks.append(self.pubsub.subscribe(f"{type}-{channels_by_type}"))
        await asyncio.gather(*tasks)

    async def add_channels_to_cache(self, channels: dict):
        for type, channels_by_type in channels.items():
            global_channels = await self.global_redis_client.get(f"{type}-channels")
            if global_channels is None:
                await self.global_redis_client.set(f"{type}-channels",json.dumps(set(channels_by_type)))
            else:
                global_channels = json.loads(global_channels)
                global_channels.extend(channels_by_type) # already a set
                await self.global_redis_client.set(f"{type}-channels",json.dumps(global_channels))
    async def unsubscribe(self, channel):
        await self.pubsub.unsubscribe(channel)

    async def wait_for_message(self):
        while True:
            message = await self.pubsub.get_message(ignore_subscribe_messages=True)
            print(message)
