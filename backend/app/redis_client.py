import redis.asyncio as aioredis
from app.config import settings

redis_client = aioredis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, decode_responses=True)