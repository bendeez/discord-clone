import redis.asyncio as aioredis
from uuid import uuid4


class RedisPubSubManager:
    """
        Initializes the RedisPubSubManager.

    Args:
        host (str): Redis server host.
        port (int): Redis server port.
    """

    def __init__(self, host, port):
        self.redis_host = host
        self.redis_port = port
        self.pubsub = None
        self.id = str(uuid4())

    async def _get_redis_connection(self) -> aioredis.Redis:
        """
        Establishes a connection to Redis.

        Returns:
            aioredis.Redis: Redis connection object.
        """
        return aioredis.Redis(host=self.redis_host,
                              port=self.redis_port,
                              auto_close_connection_pool=False)

    async def connect(self) -> None:
        """
        Connects to the Redis server and initializes the pubsub client.
        """
        self.redis_connection = await self._get_redis_connection()
        self.pubsub = self.redis_connection.pubsub()

    async def _publish(self, channel: str, message: str) -> None:
        """
        Publishes a message to a specific Redis channel.

        Args:
            room_id (str): Channel or room ID.
            message (str): Message to be published.
        """
        await self.redis_connection.publish(channel, message)

    async def subscribe(self, channel: str) -> aioredis.Redis:
        """
        Subscribes to a Redis channel.

        Args:
            room_id (str): Channel or room ID to subscribe to.

        Returns:
            aioredis.ChannelSubscribe: PubSub object for the subscribed channel.
        """
        await self.pubsub.subscribe(channel)
        return self.pubsub

    async def unsubscribe(self, channel: str) -> None:
        """
        Unsubscribes from a Redis channel.

        Args:
            room_id (str): Channel or room ID to unsubscribe from.
        """
        await self.pubsub.unsubscribe(channel)

