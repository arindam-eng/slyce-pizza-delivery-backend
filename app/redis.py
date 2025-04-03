
import redis.asyncio as redis
from app.config import settings

_redis_pool = None

async def get_redis_pool():
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = redis.ConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            decode_responses=True
        )
    return _redis_pool

async def get_redis():
    pool = await get_redis_pool()
    return redis.Redis(connection_pool=pool)