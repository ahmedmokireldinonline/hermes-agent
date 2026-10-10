import pytest
from app.tools import webhook, ToolError


@pytest.mark.asyncio
async def test_worker_webhook_allowlist_is_enforced():
    with pytest.raises(ToolError):
        await webhook("https://example.com/unsafe", {"event": "test"})
