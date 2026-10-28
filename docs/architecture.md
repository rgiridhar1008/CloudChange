# System Architecture

CloudChange uses a decoupled, modern architecture designed for Kubernetes integration.

## 1. Frontend (Presentation Layer)
- **Framework**: React 18, Vite.
- **Styling**: TailwindCSS.
- **Visuals**: `react-force-graph-2d` for rendering the blast-radius dependency graph.
- **Purpose**: Provides a dashboard to submit configuration changes, view risk scores, and manually override deployment stages.

## 2. Backend (Application Layer)
- **Framework**: FastAPI (Python 3).
- **Architecture**: Modular monolith (`app/modules/`).
- **Data Persistence**: SQLAlchemy with SQLite (`cloudchange.db`) for tracking deployment history.
- **Purpose**: Exposes REST APIs to the frontend and runs the core analytical engines deterministically.

## 3. The Orchestration Pipeline
When a user submits a change via the UI (`POST /api/v1/analyze/unified`), the Orchestrator service chains the execution in this exact order:
1. `ChangeDetector`: Parses old vs. new YAML.
2. `DependencyAnalyzer`: Queries the K8s state graph.
3. `ImpactAnalyzer`: Determines the Blast Radius.
4. `RiskEngine`: Calculates the 0-100 deterministic score.
5. `DeploymentStrategyAdvisor`: Selects the safest rollout method.
6. `AIExplanationService`: Translates the result into a human-readable string.

## 4. Kubernetes Infrastructure (Target Environment)
- CloudChange is designed to run inside or alongside a K8s cluster.
- Uses Helm for packaging user applications.
- Connects to Prometheus for live metric scraping.
- Controls deployments via simulated native K8s API commands (rolling updates, canary ingress routing).

## 5. Database Schema
Currently, persistence is handled by SQLite via SQLAlchemy.
**Table: `deployment_history`**
- `id`: Integer (PK)
- `service_name`: String
- `version`: String
- `status`: String (STARTED, IN_PROGRESS, SUCCESS, FAILED, ROLLED_BACK)
- `health_status`: String (HEALTHY, UNHEALTHY, UNKNOWN)
- `timestamp`: DateTime
- `reason`: String
