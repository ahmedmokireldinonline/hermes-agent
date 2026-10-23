import time
from collections import Counter
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from .automation_models import AuditEvent

_STARTED = time.monotonic()
_COUNTERS: Counter[str] = Counter()


def increment(name: str, amount: int = 1) -> None:
    _COUNTERS[name] += amount


def metrics() -> dict:
    return {
        'workflows_total': _COUNTERS['workflows_total'],
        'workflow_runs_total': _COUNTERS['workflow_runs_total'],
        'workflow_runs_succeeded': _COUNTERS['workflow_runs_succeeded'],
        'workflow_runs_failed': _COUNTERS['workflow_runs_failed'],
        'browser_actions_total': _COUNTERS['browser_actions_total'],
        'scrape_requests_total': _COUNTERS['scrape_requests_total'],
        'uptime_seconds': round(time.monotonic() - _STARTED, 2),
    }


async def audit(session: AsyncSession, *, event_type: str, action: str | None = None,
                run_id: str | None = None, status: str = 'ok', details: dict | None = None) -> None:
    session.add(AuditEvent(run_id=run_id, event_type=event_type, action=action,
                           status=status, details=details or {},
                           created_at=datetime.now(timezone.utc)))
    increment(f'audit_{event_type}')
