import pytest
from httpx import ASGITransport, AsyncClient
from app.api import app
from app.automation import AutomationError, validate_url, browser_run
from app.config import get_settings
from app.db import init_db


def test_private_destinations_are_blocked():
    with pytest.raises(AutomationError):
        validate_url('http://127.0.0.1:8000/internal')


def test_non_http_destinations_are_blocked():
    with pytest.raises(AutomationError):
        validate_url('file:///etc/passwd')


@pytest.mark.asyncio
async def test_workflow_step_limit_is_enforced():
    settings = get_settings()
    original = settings.max_steps
    settings.max_steps = 1
    try:
        with pytest.raises(AutomationError, match='maximum of 1 steps'):
            await browser_run([{'type': 'wait'}, {'type': 'wait'}])
    finally:
        settings.max_steps = original


@pytest.mark.asyncio
async def test_workflow_and_metrics_api():
    await init_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        created = await client.post('/workflows', json={
            'name': 'safe smoke workflow',
            'steps': [{'type': 'navigate', 'url': 'https://example.com'}],
        })
        assert created.status_code == 201
        workflow_id = created.json()['id']
        listed = await client.get('/workflows')
        assert listed.status_code == 200
        assert any(item['id'] == workflow_id for item in listed.json())
        paged = await client.get('/workflows?limit=1&offset=0')
        assert paged.status_code == 200
        assert len(paged.json()) <= 1
        metrics = await client.get('/metrics')
        assert metrics.status_code == 200
        assert 'workflow_runs_total' in metrics.json()
