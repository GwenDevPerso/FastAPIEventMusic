import os
from typing import Annotated

from fastapi import Depends
from redis import Redis

_redis_client: Redis | None = None

CACHE_TTL_SECONDS = 300
AUDIOS_LIST_CACHE_KEY = "audios:all"
AUDIOS_LIST_CACHE_TTL_SECONDS = 60


def get_redis() -> Redis:
    global _redis_client
    if _redis_client is None:
        url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        _redis_client = Redis.from_url(url, decode_responses=True)
    return _redis_client


RedisClient = Annotated[Redis, Depends(get_redis)]
