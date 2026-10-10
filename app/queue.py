import asyncio
import redis.asyncio as redis
from .config import get_settings

settings = get_settings()
PROCESSING_QUEUE = settings.redis_queue_name + ":processing"


def client():
    return redis.from_url(
        settings.redis_url, decode_responses=True, health_check_interval=30
    )


async def enqueue_task(task_id: str) -> None:
    r = client()
    try:
        await r.rpush(settings.redis_queue_name, task_id)
    finally:
        await r.aclose()


async def dequeue_task(timeout: int = 5) -> str | None:
    r = client()
    try:
        return await r.brpoplpush(
            settings.redis_queue_name, PROCESSING_QUEUE, timeout=timeout
        )
    finally:
        await r.aclose()


async def ack_task(task_id: str) -> None:
    r = client()
    try:
        await r.lrem(PROCESSING_QUEUE, 1, task_id)
    finally:
        await r.aclose()


async def retry_task(task_id: str, delay: float) -> None:
    await asyncio.sleep(min(delay, 30))
    await ack_task(task_id)
    await enqueue_task(task_id)
