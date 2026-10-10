#!/usr/bin/env python3
import argparse
import json
from app.skills import approve_skill

parser = argparse.ArgumentParser(description="Approve a reviewed candidate skill")
parser.add_argument("candidate")
parser.add_argument("--approver", required=True)
args = parser.parse_args()
print(json.dumps(approve_skill(args.candidate, args.approver), indent=2))
