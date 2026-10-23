import asyncio
import json
import time
from datetime import datetime, timezone
import redis.asyncio as redis
from sqlalchemy import select
from .config import get_settings
from .db import init_db, SessionLocal
from .automation_models import Schedule, Workflow, WorkflowRun
from .automation import run_workflow
from .tracking import audit, increment

settings = get_settings()
SCHEDULE_KEY = 'hermes:schedules'
LOCK_PREFIX = 'hermes:schedule:lock:'


def epoch(dt: datetime) -> float:
    return as_utc(dt).timestamp()


def as_utc(dt: datetime) -> datetime:
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


async def register_schedule(schedule: Schedule) -> None:
    client = redis.from_url(settings.redis_url, decode_responses=True)
    try:
        await client.zadd(SCHEDULE_KEY, {schedule.id: epoch(schedule.next_run_at)})
    finally:
        await client.aclose()


async def unregister_schedule(schedule_id: str) -> None:
    client = redis.from_url(settings.redis_url, decode_responses=True)
    try:
        await client.zrem(SCHEDULE_KEY, schedule_id)
    finally:
        await client.aclose()


async def run_due_schedule(schedule_id: str) -> None:
    client = redis.from_url(settings.redis_url, decode_responses=True)
    lock = f'{LOCK_PREFIX}{schedule_id}'
    acquired = False
    try:
        acquired = bool(await client.set(lock, str(time.time()), nx=True, ex=max(30, settings.scheduler_lease_seconds)))
        if not acquired:
            return
        async with SessionLocal() as session:
            schedule = await session.get(Schedule, schedule_id)
            if not schedule or not schedule.enabled:
                await unregister_schedule(schedule_id)
                return
            workflow = await session.get(Workflow, schedule.workflow_id)
            if not workflow:
                schedule.enabled = False
                await session.commit()
                await unregister_schedule(schedule_id)
                return
            run = WorkflowRun(workflow_id=workflow.id, status='running', started_at=datetime.now(timezone.utc))
            session.add(run)
            await session.flush()
            await audit(session, event_type='schedule_triggered', run_id=run.id, details={'schedule_id': schedule.id})
            try:
                run.outputs = await run_workflow(workflow.steps, schedule.variables or {})
                run.status = 'succeeded'
                increment('workflow_runs_succeeded')
            except Exception as exc:
                run.status = 'failed'; run.error = str(exc)
                increment('workflow_runs_failed')
                await audit(session, event_type='schedule_failed', run_id=run.id, status='failed', details={'error': str(exc)})
            run.finished_at = datetime.now(timezone.utc)
            schedule.last_run_at = run.started_at
            schedule.next_run_at = datetime.fromtimestamp(epoch(schedule.next_run_at) + schedule.interval_seconds, tz=timezone.utc)
            while as_utc(schedule.next_run_at) <= datetime.now(timezone.utc):
                schedule.next_run_at = datetime.fromtimestamp(epoch(schedule.next_run_at) + schedule.interval_seconds, tz=timezone.utc)
            await session.commit()
            await client.zadd(SCHEDULE_KEY, {schedule.id: epoch(schedule.next_run_at)})
    finally:
        if acquired:
            await client.delete(lock)
        await client.aclose()


async def scheduler_loop() -> None:
    await init_db()
    client = redis.from_url(settings.redis_url, decode_responses=True)
    try:
        while True:
            now = time.time()
            ids = await client.zrangebyscore(SCHEDULE_KEY, 0, now, start=0, num=50)
            if ids:
                await asyncio.gather(*(run_due_schedule(item) for item in ids))
            await asyncio.sleep(settings.scheduler_poll_seconds)
    finally:
        await client.aclose()


if __name__ == '__main__':
    asyncio.run(scheduler_loop())
