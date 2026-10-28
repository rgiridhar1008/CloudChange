# CloudChange Test Cases

## Part 1: Unit Testing (Backend Modules)
| ID | Module | Scenario | Expected Outcome |
|----|--------|----------|------------------|
| UT-1 | Change Detection | No changes | Return empty array |
| UT-2 | Change Detection | Replica / Memory reduction | Return array with REPLICA_REDUCTION and MEMORY_REDUCTION |
| UT-3 | Dependency Analyzer | payment-service | Impact graph includes order-service, api-gateway |
| UT-4 | Dependency Analyzer | unknown-service | Impact graph is empty |
| UT-5 | Blast Radius | Low impact depth | Criticality = LOW |
| UT-6 | Blast Radius | High impact depth (10 pods, 3 services) | Criticality = HIGH/CRITICAL |
| UT-7 | Risk Engine | Missing Probe | factor = "Missing Probe" (+15) |
| UT-8 | Risk Engine | Security Issue | factor = "Security Issue" (+10) |
| UT-9 | Deployment Advisor | LOW Risk | Strategy = ROLLING |
| UT-10 | Deployment Advisor | CRITICAL Risk | Strategy = CANARY (requires_approval = True) |
| UT-11 | Rollback Manager | Invalid service | status = NOT_FOUND |
| UT-12 | Rollback Manager | Successful state | status = ROLLBACK_COMPLETED |

## Part 2: Backend API Testing
| ID | Endpoint | Method | Scenario | Expected Outcome |
|----|----------|--------|----------|------------------|
| API-1 | `/` | GET | Root health check | 200 OK |
| API-2 | `/api/v1/analyze/unified` | POST | Valid YAML and resource | 200 OK, full pipeline JSON |
| API-3 | `/api/v1/analyze/unified` | POST | Missing manifest | 422 Unprocessable Entity |
| API-4 | `/api/v1/deployment/start` | POST | Valid start | 200 OK, status IN_PROGRESS |
| API-5 | `/api/v1/deployment/promote` | POST | Valid promote | 200 OK, percentage increased |
| API-6 | `/api/v1/deployment/status` | GET | Valid query | 200 OK |
| API-7 | `/api/v1/deployment/rollback` | POST | Valid abort | 200 OK |
| API-8 | `/api/v1/monitoring/health` | GET | Valid query | 200 OK, health status |

## Part 3-10: See `testing.md` for Infrastructure, Docker, Kubernetes, Helm, and CI/CD tests.
