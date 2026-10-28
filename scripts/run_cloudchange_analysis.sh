#!/usr/bin/env bash
# Runs the CloudChange risk engine + deployment advisor and writes
#   requires_approval=<True|False>
#   strategy=<ROLLING|CANARY|...>
# to the file given as $1 (default: stdout). $2 = changed resource name.
# Used by both GitHub Actions and GitLab CI.
set -euo pipefail

OUT_FILE="${1:-/dev/stdout}"
RESOURCE="${2:-payment-service}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/backend"

python ../scripts/generate_payload.py "$RESOURCE"

uvicorn app.main:app --host 127.0.0.1 --port 8000 > uvicorn.log 2>&1 &
SERVER_PID=$!
trap 'kill $SERVER_PID 2>/dev/null || true' EXIT

for _ in $(seq 1 30); do
  curl -sf http://127.0.0.1:8000/health >/dev/null && break
  sleep 1
done

curl -sf -X POST http://127.0.0.1:8000/api/v1/analyze/risk \
  -H "Content-Type: application/json" -d @dynamic_payload.json > risk_output.json
cat risk_output.json; echo

python - <<'PY'
import json
risk = json.load(open('risk_output.json'))
req = {
    'risk_score': risk['risk_score'],
    'risk_level': risk['risk_level'],
    'blast_radius': risk['blast_radius'],
    'affected_services': risk['affected_services'],
    'criticality': risk['blast_radius']['criticality'],
}
json.dump(req, open('deploy_req.json', 'w'))
PY

curl -sf -X POST http://127.0.0.1:8000/api/v1/deployment/recommendation \
  -H "Content-Type: application/json" -d @deploy_req.json > deploy_output.json
cat deploy_output.json; echo

python - "$OUT_FILE" <<'PY'
import json, sys
d = json.load(open('deploy_output.json'))
with open(sys.argv[1], 'a') as f:
    f.write(f"requires_approval={d.get('requires_approval', False)}\n")
    f.write(f"strategy={d.get('strategy', 'ROLLING')}\n")
PY
