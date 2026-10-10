#!/usr/bin/env python3
import argparse
import asyncio
import json
from app.skills import import_external_skill

parser = argparse.ArgumentParser(
    description="Import an external skill as an untrusted candidate"
)
parser.add_argument("url")
parser.add_argument("--name", default=None)
args = parser.parse_args()

try:
    print(
        json.dumps(
            asyncio.run(import_external_skill(args.url, args.name)),
            ensure_ascii=False,
            indent=2,
        )
    )
except Exception as exc:
    raise SystemExit(f"Import failed: {exc}")
