import os
os.environ['MOCK_LLM'] = 'true'
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///./test-hermes.db'
os.environ['QUEUE_MODE'] = 'inline'

import pytest
from httpx import ASGITransport, AsyncClient
from app.api import app
from app.db import init_db

@pytest.mark.asyncio
async def test_health():
    await init_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        response = await client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] in {'ok', 'degraded'}

@pytest.mark.asyncio
async def test_create_and_get_task():
    await init_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        created = await client.post('/tasks', json={'input': 'Write a short English follow-up message'})
        assert created.status_code == 202
        task = created.json()
        assert task['status'] == 'succeeded'
        fetched = await client.get(f"/tasks/{task['id']}")
        assert fetched.status_code == 200
        assert fetched.json()['id'] == task['id']
