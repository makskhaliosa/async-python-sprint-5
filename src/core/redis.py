from redis.asyncio import Redis

from .settings import app_settings


redis_client = Redis(
    host=app_settings.REDIS_HOST,
    port=app_settings.REDIS_PORT,
    decode_responses=True,
    protocol=3
)
