# CloudChange

CloudChange is a comprehensive Kubernetes continuous deployment risk engine. It intercepts developer configuration changes (e.g., Helm chart modifications) and deterministically analyzes the blast radius, calculates a risk score, and automates safe deployment strategies (like Canary releases) with integrated health monitoring and automatic rollback mechanisms.

## Project Status
**Phase 17 - COMPLETE**

CloudChange successfully integrates a React SPA frontend, a FastAPI Python backend, an AI Contextualization layer, and robust orchestration connecting dependency analysis, risk calculations, and deployment engines.

## Key Features
* **Change Detection**: Identifies dangerous modifications (e.g., dropped probes, replica reductions).
* **Dependency & Blast Radius Analysis**: Constructs a graph to visualize impacted upstream/downstream services.
* **Deterministic Risk Engine**: Generates a 0-100 Risk Score based on fixed, transparent rules.
* **Deployment Advisor**: Recommends Rolling, Canary, or manual-approval deployments based on risk.
* **Canary Engine**: Splits traffic progressively (10% → 25% → 50% → 100%).
* **Health Monitoring & Auto-Rollback**: Connects to Prometheus to monitor CPU, memory, and error rates during a deployment, aborting and rolling back if thresholds are exceeded.
* **AI Explanation**: Non-decision-making LLM integration to translate numerical risk scores into human-readable insights.

## Quick Start

### Backend (Python)
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
*Note: The SQLite database (`cloudchange.db`) is auto-generated.*

### Frontend (React)
```bash
cd frontend
npm install
npm run dev
```

## Documentation Directory
- [Architecture](docs/architecture.md)
- [Modules & Responsibilities](docs/modules.md)
- [API Reference](docs/api.md)
- [Deployment & Rollback Strategy](docs/deployment.md)
- [Testing & Research](docs/testing.md)
## Testing and Verification
The complete CloudChange testing phase includes Python unit tests, API tests, and infrastructure testing (Docker/Kubernetes).

### 1. Backend, API, and End-to-End Tests
```bash
cd backend
python -m venv venv
# Activate the venv (Windows: venv\Scripts\activate, Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
pytest tests/test_modules.py -v
pytest tests/test_api.py -v
pytest tests/test_scenarios.py -v
```

### 2. Frontend Tests
```bash
cd frontend
npm install
npm run dev
# Then open http://localhost:5173 to manually verify UI components.
```

### 3. Docker Testing
```bash
docker build -t cloudchange-backend ./backend
docker build -t cloudchange-frontend ./frontend
```

### 4. Kubernetes & Helm Testing
```bash
minikube start
kubectl apply -f ./k8s/namespace.yaml
helm lint ./helm/cloudchange
```

### 5. Complete Demo (End-to-End Failure Testing)
Run the automated failure simulation which directly benchmarks conventional vs. CloudChange-assisted deployment strategies:
```bash
cd backend
python experiments/run_experiment.py
```
This script will produce an empirical `results.json` showing the exact latency and downtime mitigation.
