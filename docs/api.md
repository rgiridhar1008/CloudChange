# API Reference

All backend APIs are prefixed with `/api/v1`.

## Analysis & Orchestration

### `POST /api/v1/analyze/unified`
Executes the complete CloudChange analysis pipeline end-to-end.
**Payload:**
```json
{
  "manifest_content": "apiVersion: apps/v1\nkind: Deployment...",
  "resource_name": "payment-service"
}
```
**Response:** Returns a comprehensive JSON object containing:
- `changes`: Array of detected diffs.
- `impact`: Graph tracing and blast radius depth.
- `risk`: The deterministic 0-100 score and specific rule factors.
- `recommendation`: Target strategy (Canary, Rolling) and AI explanation.

---

## Deployment Execution

### `POST /api/v1/deployment/start`
Initiates a deployment using the recommended strategy.
**Payload:**
```json
{
  "service_name": "payment-service",
  "new_version": "v2.0"
}
```

### `POST /api/v1/deployment/promote`
Progresses a Canary deployment to the next traffic tier (e.g., 10% -> 25%). Returns an error if health metrics are failing.
**Payload:**
```json
{
  "service_name": "payment-service"
}
```

### `GET /api/v1/deployment/status?service_name=...`
Returns the active state of a deployment (e.g., IN_PROGRESS, HEALTHY, FAILED).

### `POST /api/v1/deployment/rollback`
Forcefully aborts the current rollout and restores the previous stable version from the database.
**Payload:**
```json
{
  "service_name": "payment-service"
}
```

---

## Monitoring

### `GET /api/v1/monitoring/health?service_name=...`
Polls the Prometheus integration and evaluates current CPU, Memory, and Error Rate against defined rules. Returns `HEALTHY` or `UNHEALTHY`.
