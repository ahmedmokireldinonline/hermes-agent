import redis.asyncio as redis
from .config import get_settings

settings = get_settings()

async def enqueue_task(task_id: str) -> None:
    client = redis.from_url(settings.redis_url, decode_responses=True)
    try:
        await client.rpush(settings.redis_queue_name, task_id)
    finally:
        await client.aclose()

async def dequeue_task(timeout: int = 5) -> str | None:
    client = redis.from_url(settings.redis_url, decode_responses=True)
    try:
        item = await client.blpop(settings.redis_queue_name, timeout=timeout)
        return item[1] if item else None
    finally:
        await client.aclose()
