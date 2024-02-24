from redis.asyncio import Redis

from .settings import app_settings

HOST = (
    app_settings.REDIS_HOST_TEST
    if app_settings.TESTING
    else app_settings.REDIS_HOST
)

redis_client = Redis(
    host=HOST,
    port=app_settings.REDIS_PORT,
    decode_responses=True,
    protocol=3
)
