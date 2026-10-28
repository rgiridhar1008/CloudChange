#!/usr/bin/env python3
"""Writes a GitLab child pipeline: manual approval gate if the advisor requires it, automatic otherwise."""
import sys

requires_approval = sys.argv[1].strip().lower() == "true"
strategy = sys.argv[2].strip()

env = "production-approval" if requires_approval else "development"
manual = "  when: manual\n  allow_failure: false\n" if requires_approval else ""

print(f"""stages: [deploy]

deploy:
  stage: deploy
  image: alpine:3.20
  environment:
    name: {env}
{manual}  script:
    - echo "Deployment strategy: {strategy}"
    - echo "Requires approval: {requires_approval}"
    - echo "Deployment logic simulated."
""")
