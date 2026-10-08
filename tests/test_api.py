import os

os.environ.update(
    {
        "ENV": "dev",
        "MOCK_LLM": "true",
        "DATABASE_URL": "sqlite+aiosqlite:///./test-hermes.db",
        "QUEUE_MODE": "inline",
        "API_KEYS": "test-secret",
        "RATE_LIMIT_PER_MIN": "60",
    }
)
import pytest
from httpx import ASGITransport, AsyncClient
from app.api import app
from app.db import init_db


@pytest.mark.asyncio
async def test_health():
    await init_db()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_auth_and_task_ownership():
    await init_db()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        assert (await client.post("/tasks", json={"input": "x"})).status_code == 401
        created = await client.post(
            "/tasks",
            headers={"X-API-Key": "test-secret"},
            json={
                "input": "Write a short English follow-up message",
                "idempotency_key": "case-1",
            },
        )
        assert created.status_code == 202
        task = created.json()
        duplicate = await client.post(
            "/tasks",
            headers={"X-API-Key": "test-secret"},
            json={"input": "different", "idempotency_key": "case-1"},
        )
        assert duplicate.json()["id"] == task["id"]
        assert (
            await client.get(f"/tasks/{task['id']}", headers={"X-API-Key": "other"})
        ).status_code == 401
        assert (
            await client.get(
                f"/tasks/{task['id']}", headers={"X-API-Key": "test-secret"}
            )
        ).status_code == 200


@pytest.mark.asyncio
async def test_unknown_fields_rejected():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/tasks",
            headers={"X-API-Key": "test-secret"},
            json={"input": "x", "admin": True},
        )
    assert response.status_code == 422
