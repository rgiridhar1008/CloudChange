# CI/CD Setup with CloudChange

This repository uses GitHub Actions to integrate CloudChange's Risk Engine and Deployment Strategy Advisor natively into the continuous delivery pipeline.

## Pipeline Architecture

1. **build-and-test**:
   - Runs `npm build` for the frontend.
   - Runs `pytest` for the backend.
2. **docker-build-scan**:
   - Builds Docker images.
   - Uses **AquaSec Trivy** to scan for vulnerabilities (configured to fail on CRITICAL or HIGH severity issues).
3. **helm-validation**:
   - Runs `helm lint` and `helm template` to ensure Kubernetes manifests are valid.
4. **cloudchange-analysis**:
   - Uses our custom Change Detection and Risk Engine to evaluate the incoming changes.
   - Extracts the required `requires_approval` boolean and `strategy` (Rolling/Canary/Blue-Green) from our Deployment Strategy Advisor API.
5. **deployment-decision**:
   - A conditional deployment job that maps to GitHub Environments.
   - If `requires_approval` is `True`, it maps to the `production-approval` environment, triggering manual review rules configured in GitHub.

## Required Setup in GitHub

### 1. Environments

You must create two Environments in your GitHub Repository settings (`Settings` -> `Environments`):

- **`development`**: 
  - No special rules.
- **`production-approval`**:
  - Check the box for **"Required reviewers"**.
  - Add specific teams or developers who are allowed to approve high-risk (HIGH/CRITICAL) configuration changes.

### 2. Secrets

If you plan to push the Docker images to a registry or deploy to AWS in the future, add the following secrets:
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

Currently, the pipeline is configured for local simulation and does not require these keys, as it will not push to a live registry or cluster.

## Local Development (Minikube)

This CI/CD pipeline does not break local development. You can continue using:
```bash
minikube start
helm install cloudchange-demo ./helm/cloudchange-demo
```
The CI/CD pipeline will act as a safety net in PRs to ensure risky config isn't merged blindly.
