"""Safe Evolver: proposals only, never automatic code/prompt/skill promotion."""

import asyncio
import json
from pathlib import Path
from datetime import datetime, timezone
from .config import get_settings

settings = get_settings()


async def collect_candidates() -> list[dict]:
    return []


async def run_once() -> dict:
    candidates = await collect_candidates()
    review_dir = Path(settings.review_dir).resolve()
    review_dir.mkdir(parents=True, exist_ok=True)
    proposal = (
        review_dir
        / f"proposal-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    )
    proposal.write_text(
        json.dumps(
            {
                "candidates": candidates,
                "promoted": False,
                "reason": "Human review required",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return {"candidates": candidates, "promoted": False, "proposal": str(proposal)}


async def main() -> None:
    while True:
        await run_once()
        await asyncio.sleep(6 * 60 * 60)


if __name__ == "__main__":
    asyncio.run(main())
