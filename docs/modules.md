# Module Responsibilities

The backend logic is strictly decoupled into single-responsibility modules located in `backend/app/modules/`.

### 1. `change_detection`
Parses raw YAML manifests and determines explicit diffs (e.g., Replicas changed from 3 to 1). 

### 2. `dependency_analysis`
Constructs a directed graph of services (e.g., Ingress → API Gateway → Order Service → Database).
- **ImpactAnalyzer**: Traces upstream dependencies to calculate blast radius depth.

### 3. `risk_analysis`
The heart of the deterministic engine.
- **BlastRadiusCalculator**: Translates impact depth and traffic exposure into a discrete level (LOW, HIGH, CRITICAL).
- **RiskEngine**: Applies hardcoded rules (e.g., Missing Probe = +15, Memory Reduction = +20) to generate a final out-of-100 score.

### 4. `deployment_strategy`
Maps the final risk score to an actionable K8s deployment plan:
- **0-30**: Rolling Deployment
- **31-80**: Canary Deployment
- **81-100**: Canary/Blue-Green with explicit Human Approval Required.

### 5. `canary_deployment`
The execution engine.
- **DeploymentEngine**: Handles the step-by-step traffic shifting.
- **RollbackManager**: Interfaces with the SQLite DB to record state and executes fallbacks to prior versions if health checks fail.

### 6. `monitoring`
- **MonitoringService**: Bridges CloudChange to Prometheus, fetching live telemetry (CPU, Memory, Latency, Error Rates).
- **HealthEvaluatorRules**: Asserts metrics against safety thresholds (e.g., `error_rate > 5% == UNHEALTHY`).

### 7. `ai_explanation`
An isolated abstraction layer that leverages an LLM (e.g., OpenAI) to read the deterministic outputs of the modules above and generate a simple English explanation. **It is strictly barred from making deployment decisions.** Includes a hardcoded fallback if the LLM API is unavailable.
