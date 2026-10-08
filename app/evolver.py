"""Conservative Evolver entry point.

This MVP intentionally does not auto-promote prompts. It only reports candidates;
promotion must be implemented with dev/holdout tests and human or policy approval.
"""
import asyncio
from .config import get_settings

settings = get_settings()

async def collect_candidates() -> list[dict]:
    return []

async def run_once() -> dict:
    candidates = await collect_candidates()
    return {'candidates': candidates, 'promoted': False, 'reason': 'MVP keeps automatic promotion disabled'}

async def main() -> None:
    while True:
        await run_once()
        await asyncio.sleep(6 * 60 * 60)

if __name__ == '__main__':
    asyncio.run(main())
