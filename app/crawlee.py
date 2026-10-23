import json
from uuid import uuid4
import redis.asyncio as redis
from .config import get_settings
from .tracking import increment

settings = get_settings()
CRAWL_QUEUE = 'hermes:crawler:jobs'
RESULT_PREFIX = 'hermes:crawler:result:'


async def enqueue_crawl(start_urls: list[str], selector: str, max_requests: int) -> str:
    job_id = str(uuid4())
    client = redis.from_url(settings.redis_url, decode_responses=True)
    try:
        await client.rpush(CRAWL_QUEUE, json.dumps({'id': job_id, 'start_urls': start_urls, 'selector': selector, 'max_requests': max_requests}))
        increment('crawl_jobs_queued')
        return job_id
    finally:
        await client.aclose()


async def get_crawl_result(job_id: str) -> dict | None:
    client = redis.from_url(settings.redis_url, decode_responses=True)
    try:
        raw = await client.get(f'{RESULT_PREFIX}{job_id}')
        return json.loads(raw) if raw else None
    finally:
        await client.aclose()
