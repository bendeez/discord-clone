import redis.asyncio as aioredis


class RedisPubSubManager:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.redis_connection = None
        self.pubsub = None

    def connect(self):
        self.redis_connection = aioredis.Redis(host=self.host, port=self.port,
                                     db=0, decode_responses=True)
        self.pubsub = self.redis_connection.pubsub()

    async def publish(self, topic, data):
        await self.redis_connection.publish(topic, data)

    async def subscribe(self, topic):
        await self.pubsub.subscribe(topic)

    async def unsubscribe(self, topic):
        await self.pubsub.unsubscribe(topic)
