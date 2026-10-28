# Final Project Demonstration Script

Follow this script to demonstrate the complete, end-to-end functionality of CloudChange to your professors or evaluators.

## Prerequisites
1. Open Terminal 1: Run the backend `cd backend && uvicorn app.main:app`
2. Open Terminal 2: Run the frontend `cd frontend && npm run dev`
3. Open a browser to `http://localhost:5173`.

---

## Step 1: The Healthy Application
**Action**: Navigate to the UI and show the clean state. 
**Talking Point**: "CloudChange is currently monitoring our live Kubernetes cluster. Everything is healthy."

## Step 2: The Developer Change
**Action**: On the `Change Analysis` page, go to the YAML Editor.
- Change `resource_name` to: `unhealthy-payment-service` *(The "unhealthy" prefix tells our mock monitoring system to simulate a failing application)*
- Change `replicas: 3` to `replicas: 1`
- Remove the `livenessProbe` block entirely.
**Talking Point**: "A developer just committed a dangerous change: dropping redundancy to 1 replica and deleting the health probe."

## Step 3 & 4: Detection and Dependency Graph
**Action**: Click **Analyze Impact & Risk**.
**Talking Point**: "CloudChange intercepts the commit. It detects the specific diffs and queries the Dependency Graph. Because it is the Payment Service, it identifies that the Order Service and API Gateway are now caught in the Blast Radius."

## Step 5: Risk Score Calculation
**Action**: Point to the **Risk Engine Verdict** card on the screen.
**Talking Point**: "The deterministic risk engine calculates a score. Because replicas were dropped (+20), probes removed (+15), and it hits external traffic (+15), the score evaluates to **CRITICAL**."

## Step 6: Canary Recommendation
**Action**: Point to the **Deployment Advisor** card on the screen.
**Talking Point**: "Based on this High Risk, the engine refuses a rolling update. It mandates a **CANARY** strategy, and explicitly flags that 'APPROVAL IS REQUIRED'."
*(Optional: Read the AI Explanation generated on the screen to show how the numbers are translated into plain English).*

## Step 7: Canary Begins
**Action**: Click **Proceed to Deployment**. Click **Start Deployment**.
**Talking Point**: "We initiate the deployment. It begins routing exactly 10% of traffic to the new dangerous v2 version."

## Step 8 & 9: Failure Simulated & Detected
**Action**: The screen will rapidly update. Wait for the status to change.
**Talking Point**: "Because we named it 'unhealthy-payment-service', our Prometheus monitoring hooks instantly detect that the error rate threshold has been breached on that 10% traffic slice."

## Step 10 & 11: Deployment Stops & Rollback Occurs
**Action**: Watch the UI auto-update to a red `ROLLED_BACK` status.
**Talking Point**: "The Deployment Engine halts the Canary promotion. The Rollback Manager queries the SQLite database for the last stable version (v1) and automatically reverts the cluster to safety."

## Step 12: Dashboard Displays the Result
**Action**: Navigate to the `Deployment History` or `Overview` tab (if configured) or simply show the final state on the Deployment Control screen.
**Talking Point**: "The dashboard now permanently reflects this averted crisis in the deployment history. 90% of our users never even noticed there was a problem."
