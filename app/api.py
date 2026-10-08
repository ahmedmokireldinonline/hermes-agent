from contextlib import asynccontextmanager
from fastapi import FastAPI, Header, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from .config import get_settings
from .db import init_db, SessionLocal, Task, get_task
from .schemas import TaskCreate, TaskResponse, HealthResponse
from .agent import run_agent
from .queue import enqueue_task

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title=settings.app_name, version='0.1.0', lifespan=lifespan)

def authenticate(x_api_key: str | None = Header(default=None)):
    if settings.allowed_api_keys and x_api_key not in settings.allowed_api_keys:
        raise HTTPException(status_code=401, detail='Invalid API key')

@app.get('/health', response_model=HealthResponse)
async def health():
    db_status = 'ok'
    try:
        async with SessionLocal() as session:
            await session.execute(select(Task).limit(1))
    except Exception:
        db_status = 'down'
    return HealthResponse(status='ok' if db_status == 'ok' else 'degraded', database=db_status, redis='not_configured', llm='mock' if settings.mock_llm else 'ollama')

@app.post('/tasks', response_model=TaskResponse, status_code=202, dependencies=[Depends(authenticate)])
async def create_task(payload: TaskCreate):
    async with SessionLocal() as session:
        if payload.idempotency_key:
            existing = (await session.execute(select(Task).where(Task.idempotency_key == payload.idempotency_key))).scalar_one_or_none()
            if existing:
                return existing
        task = Task(input=payload.input, idempotency_key=payload.idempotency_key, status='queued')
        session.add(task)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise HTTPException(status_code=409, detail='Duplicate idempotency key')
        await session.refresh(task)
        if settings.queue_mode == 'inline':
            try:
                outcome = await run_agent(task.input)
                task.role = outcome['role']; task.result = outcome['result']; task.steps = outcome['steps']
                evaluation = outcome['evaluation']; task.score = evaluation.get('overall'); task.critique = evaluation.get('critique'); task.reusable = bool(evaluation.get('reusable', False)); task.status = 'succeeded'
            except Exception as exc:
                task.status = 'failed'; task.failure_reason = str(exc)
        else:
            await enqueue_task(task.id)
        await session.commit()
        await session.refresh(task)
        return task

@app.get('/tasks/{task_id}', response_model=TaskResponse, dependencies=[Depends(authenticate)])
async def get_task_endpoint(task_id: str):
    async with SessionLocal() as session:
        task = await get_task(session, task_id)
        if not task:
            raise HTTPException(status_code=404, detail='Task not found')
        return task
