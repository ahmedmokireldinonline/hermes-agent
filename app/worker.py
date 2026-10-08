import asyncio
from .config import get_settings
from .db import init_db, SessionLocal, get_task
from .agent import run_agent
from .queue import dequeue_task

settings = get_settings()

async def process(task_id: str) -> None:
    async with SessionLocal() as session:
        task = await get_task(session, task_id)
        if not task or task.status in {'succeeded', 'cancelled'}:
            return
        task.status = 'running'
        await session.commit()
        try:
            outcome = await asyncio.wait_for(run_agent(task.input), timeout=settings.max_task_seconds)
            task.role = outcome['role']; task.result = outcome['result']; task.steps = outcome['steps']
            evaluation = outcome['evaluation']; task.score = evaluation.get('overall'); task.critique = evaluation.get('critique'); task.reusable = bool(evaluation.get('reusable', False)); task.status = 'succeeded'
        except Exception as exc:
            task.retries += 1
            task.failure_reason = str(exc)
            task.status = 'dead_letter' if task.retries >= settings.max_retries else 'failed'
        await session.commit()

async def main() -> None:
    await init_db()
    while True:
        task_id = await dequeue_task(timeout=5)
        if task_id:
            await process(task_id)
        else:
            await asyncio.sleep(settings.worker_poll_seconds)

if __name__ == '__main__':
    asyncio.run(main())
