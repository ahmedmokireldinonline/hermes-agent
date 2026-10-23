from contextlib import asynccontextmanager
from datetime import datetime, timezone
from time import monotonic
from fastapi import FastAPI, Header, HTTPException, Depends
from sqlalchemy import select, desc
from sqlalchemy.exc import IntegrityError
from .config import get_settings
from .db import init_db, SessionLocal, Task, get_task
from .schemas import TaskCreate, TaskResponse, HealthResponse
from .agent import run_agent
from .queue import enqueue_task
from .automation import scrape, run_workflow, AutomationError
from .automation_models import Workflow, WorkflowRun, AuditEvent
from .automation_schemas import (WorkflowCreate, WorkflowResponse, WorkflowRunCreate,
    WorkflowRunResponse, ScrapeRequest, MetricsResponse)
from .tracking import audit, increment, metrics

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title=settings.app_name, version='0.2.0', lifespan=lifespan,
              description='Self-hosted agentic automation: tasks, browser workflows, scraping, and observability.')


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
    return HealthResponse(status='ok' if db_status == 'ok' else 'degraded', database=db_status,
                          redis='configured' if settings.queue_mode == 'redis' else 'inline',
                          llm='mock' if settings.mock_llm else 'ollama')


@app.get('/metrics', response_model=MetricsResponse, dependencies=[Depends(authenticate)])
async def get_metrics():
    return metrics()


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


@app.post('/workflows', response_model=WorkflowResponse, status_code=201, dependencies=[Depends(authenticate)])
async def create_workflow(payload: WorkflowCreate):
    async with SessionLocal() as session:
        workflow = Workflow(name=payload.name, description=payload.description,
                            steps=[step.model_dump(exclude_none=True) for step in payload.steps])
        session.add(workflow)
        await session.commit()
        await session.refresh(workflow)
        increment('workflows_total')
        return workflow


@app.get('/workflows', response_model=list[WorkflowResponse], dependencies=[Depends(authenticate)])
async def list_workflows():
    async with SessionLocal() as session:
        return list((await session.execute(select(Workflow).order_by(desc(Workflow.created_at)))).scalars())


@app.get('/workflows/{workflow_id}', response_model=WorkflowResponse, dependencies=[Depends(authenticate)])
async def get_workflow(workflow_id: str):
    async with SessionLocal() as session:
        workflow = await session.get(Workflow, workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail='Workflow not found')
        return workflow


@app.post('/workflows/{workflow_id}/runs', response_model=WorkflowRunResponse, status_code=202, dependencies=[Depends(authenticate)])
async def run_workflow_endpoint(workflow_id: str, payload: WorkflowRunCreate):
    async with SessionLocal() as session:
        workflow = await session.get(Workflow, workflow_id)
        if not workflow or workflow.status != 'active':
            raise HTTPException(status_code=404, detail='Active workflow not found')
        run = WorkflowRun(workflow_id=workflow.id, status='running', started_at=datetime.now(timezone.utc))
        session.add(run)
        await session.flush()
        started = monotonic()
        increment('workflow_runs_total')
        await audit(session, event_type='workflow_started', run_id=run.id, details={'workflow_id': workflow.id})
        try:
            result = await run_workflow(workflow.steps, payload.variables)
            run.status = 'succeeded'; run.outputs = result
            increment('workflow_runs_succeeded')
            await audit(session, event_type='workflow_completed', run_id=run.id, details={'steps': len(workflow.steps)})
        except (AutomationError, Exception) as exc:
            run.status = 'failed'; run.error = str(exc)
            increment('workflow_runs_failed')
            await audit(session, event_type='workflow_failed', run_id=run.id, status='failed', details={'error': str(exc)})
        run.finished_at = datetime.now(timezone.utc)
        run.duration_ms = int((monotonic() - started) * 1000)
        await session.commit()
        await session.refresh(run)
        return run


@app.get('/workflows/{workflow_id}/runs', response_model=list[WorkflowRunResponse], dependencies=[Depends(authenticate)])
async def list_workflow_runs(workflow_id: str):
    async with SessionLocal() as session:
        return list((await session.execute(select(WorkflowRun).where(WorkflowRun.workflow_id == workflow_id).order_by(desc(WorkflowRun.created_at)))).scalars())


@app.post('/scrape', dependencies=[Depends(authenticate)])
async def scrape_endpoint(payload: ScrapeRequest):
    try:
        async with SessionLocal() as session:
            result = await scrape(payload.model_dump())
            await audit(session, event_type='scrape_completed', action='scrape', details={'url': payload.url, 'use_browser': payload.use_browser})
            await session.commit()
            return result
    except AutomationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get('/audit-events', dependencies=[Depends(authenticate)])
async def audit_events(limit: int = 100):
    limit = max(1, min(limit, 500))
    async with SessionLocal() as session:
        rows = (await session.execute(select(AuditEvent).order_by(desc(AuditEvent.created_at)).limit(limit))).scalars()
        return list(rows)
