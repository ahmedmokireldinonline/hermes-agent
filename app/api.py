import hmac
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from fastapi import FastAPI, Header, HTTPException, Request, Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from .config import get_settings, ROOT
from .db import init_db, SessionLocal, Task, get_task
from .schemas import TaskCreate, TaskResponse, HealthResponse
from .agent import run_agent
from .queue import enqueue_task

settings = get_settings()
_hits: dict[str, deque[float]] = defaultdict(deque)


def owner_from_key(x_api_key: str | None) -> str:
    if not settings.allowed_api_keys:
        return "dev"
    if not x_api_key or not any(
        hmac.compare_digest(x_api_key, key) for key in settings.allowed_api_keys
    ):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return x_api_key


def enforce_rate_limit(owner: str) -> None:
    now = time.monotonic()
    bucket = _hits[owner]
    while bucket and now - bucket[0] >= 60:
        bucket.popleft()
    if len(bucket) >= settings.rate_limit_per_min:
        raise HTTPException(
            status_code=429, detail="Rate limit exceeded", headers={"Retry-After": "60"}
        )
    bucket.append(now)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title=settings.app_name, version="0.2.0", lifespan=lifespan)


@app.middleware("http")
async def request_size_limit(request: Request, call_next):
    length = request.headers.get("content-length")
    if length and int(length) > settings.request_max_bytes:
        return Response(
            content='{"detail":"Request too large"}',
            status_code=413,
            media_type="application/json",
        )
    return await call_next(request)


@app.get("/health", response_model=HealthResponse)
async def health():
    try:
        async with SessionLocal() as session:
            await session.execute(select(Task).limit(1))
        db_status = "ok"
    except Exception:
        db_status = "down"
    return HealthResponse(
        status="ok" if db_status == "ok" else "degraded",
        database=db_status,
        redis="configured" if settings.queue_mode == "redis" else "not_configured",
        llm="mock" if settings.mock_llm else "ollama",
    )


@app.get("/ready", response_model=HealthResponse)
async def ready():
    result = await health()
    if result.database != "ok":
        raise HTTPException(status_code=503, detail="Not ready")
    return result


@app.post("/tasks", response_model=TaskResponse, status_code=202)
async def create_task(
    payload: TaskCreate, x_api_key: str | None = Header(default=None)
):
    owner = owner_from_key(x_api_key)
    enforce_rate_limit(owner)
    async with SessionLocal() as session:
        if payload.idempotency_key:
            existing = (
                await session.execute(
                    select(Task).where(
                        Task.owner_key == owner,
                        Task.idempotency_key == payload.idempotency_key,
                    )
                )
            ).scalar_one_or_none()
            if existing:
                return existing
        task = Task(
            owner_key=owner,
            input=payload.input,
            idempotency_key=payload.idempotency_key,
            status="queued",
        )
        session.add(task)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            existing = (
                await session.execute(
                    select(Task).where(
                        Task.owner_key == owner,
                        Task.idempotency_key == payload.idempotency_key,
                    )
                )
            ).scalar_one_or_none()
            if existing:
                return existing
            raise HTTPException(status_code=409, detail="Task could not be created")
        await session.refresh(task)
        if settings.queue_mode == "inline":
            try:
                outcome = await run_agent(task.input)
                task.role = outcome["role"]
                task.result = outcome["result"]
                task.steps = outcome["steps"]
                evaluation = outcome["evaluation"]
                task.score = evaluation.get("overall")
                task.critique = evaluation.get("critique")
                task.reusable = bool(evaluation.get("reusable", False))
                task.status = "succeeded"
            except Exception:
                task.status = "failed"
                task.failure_reason = "Task execution failed"
        else:
            await enqueue_task(task.id)
        await session.commit()
        await session.refresh(task)
        return task


@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_endpoint(task_id: str, x_api_key: str | None = Header(default=None)):
    owner = owner_from_key(x_api_key)
    async with SessionLocal() as session:
        task = await get_task(session, task_id, owner)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task


if (ROOT / "web").is_dir():
    app.mount("/", StaticFiles(directory=ROOT / "web", html=True), name="web")
