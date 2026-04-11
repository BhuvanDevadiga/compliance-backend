import os

import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True,  
    socket_timeout=5,
    socket_connect_timeout=5,
    retry_on_timeout=True,
    health_check_interval=30,
)


def close_redis_client() -> None:
    close = getattr(redis_client, "close", None)
    if callable(close):
        close()

    pool = getattr(redis_client, "connection_pool", None)
    if pool is not None:
        pool.disconnect()
