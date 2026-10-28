# Deployment and Rollback Strategy

CloudChange relies on a dynamic, risk-adjusted deployment approach to prevent severe outages.

## Deployment Strategies

1. **Rolling Deployment (Low Risk)**
   - Used when risk scores are 0-30.
   - Traditional Kubernetes rolling update. Pods are replaced one by one.

2. **Canary Deployment (Medium - High Risk)**
   - Used when risk scores are 31-80.
   - Traffic is systematically shifted from the stable version (v1) to the new version (v2).
   - **Tiers**: 10% → 25% → 50% → 100%.
   - At each tier, CloudChange queries Prometheus metrics. If metrics fail, the deployment freezes.

3. **Manual Approval (Critical Risk)**
   - Used when risk scores > 80.
   - The pipeline hard-stops and requires a human operator to click "Approve" before initiating a Canary or Blue-Green deployment.

## Health Evaluation
The `HealthEvaluatorRules` module checks the following per service:
- Error Rate > Threshold?
- Latency > Threshold?
- Pod Restart Count > Threshold?
- Pod Readiness = False?

## Automatic Rollback Mechanism
1. If a Canary step (e.g., 10%) reports an `UNHEALTHY` status.
2. The `DeploymentEngine` aborts the rollout.
3. The `RollbackManager` fetches the `DeploymentHistory` from the SQLite database.
4. It issues a simulated `helm rollback` or `kubectl rollout undo` command to revert the cluster state to the known-good version.
5. The `deployment_history` table is updated with the `ROLLED_BACK` status to prevent endless crash-loops.
