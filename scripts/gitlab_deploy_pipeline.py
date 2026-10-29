#!/usr/bin/env python3
"""Writes a GitLab child pipeline: manual approval gate if the advisor requires it, automatic otherwise."""
import sys
import yaml

raw_approval = sys.argv[1].strip().splitlines()[0] if len(sys.argv) > 1 and sys.argv[1].strip() else "false"
requires_approval = raw_approval.lower() in ("true", "1", "yes")

strategy = sys.argv[2].strip().splitlines()[0] if len(sys.argv) > 2 and sys.argv[2].strip() else "ROLLING"

env_name = "production-approval" if requires_approval else "development"

job = {
    "stage": "deploy",
    "image": "alpine:3.20",
    "environment": {
        "name": env_name
    }
}

if requires_approval:
    job["when"] = "manual"
    job["allow_failure"] = False

job["script"] = [
    f'echo "Deployment strategy: {strategy}"',
    f'echo "Requires approval: {requires_approval}"',
    'echo "Deployment logic simulated."'
]

pipeline = {
    "stages": ["deploy"],
    "execute-deploy": job
}

print(yaml.safe_dump(pipeline, sort_keys=False, default_flow_style=False))
