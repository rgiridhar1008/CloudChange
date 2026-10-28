# CloudChange Demo Helm Chart

This Helm chart deploys the sample microservices application (Frontend, API Gateway, Order, Payment, User, and PostgreSQL) to Kubernetes. It is designed to be fully configurable via `values.yaml` so that CloudChange can analyze configuration changes dynamically.

## Structure

* `Chart.yaml`: Chart metadata.
* `values.yaml`: Base configuration for all microservices. **(CloudChange Analysis Target)**
* `values-dev.yaml`: Overrides for a development environment (e.g., `replicaCount: 1`).
* `values-prod.yaml`: Overrides for a production environment (e.g., `replicaCount: 5`, higher resources).
* `templates/`: Contains dynamic Kubernetes manifests.

## Usage

### 1. Verification (Lint & Template)
Before installing, you should verify the chart is well-formed:

```bash
# Navigate to the helm directory
cd helm

# Lint the chart for errors
helm lint ./cloudchange-demo

# Dry-run template generation to preview the exact YAML that will be sent to K8s
helm template my-release ./cloudchange-demo
```

### 2. Dry-Run Installation
Test the installation process without actually modifying the cluster:
```bash
helm install my-release ./cloudchange-demo --dry-run
```

### 3. Installation
Deploy the application using the default `values.yaml`:
```bash
helm install my-release ./cloudchange-demo -n cloudchange-test --create-namespace
```

To deploy with environment overrides:
```bash
# Development
helm install my-release ./cloudchange-demo -f ./cloudchange-demo/values-dev.yaml -n cloudchange-dev --create-namespace

# Production
helm install my-release ./cloudchange-demo -f ./cloudchange-demo/values-prod.yaml -n cloudchange-prod --create-namespace
```

### 4. Upgrade and Rollback
If you modify `values.yaml` (e.g., changing a replica count), you can upgrade the release:
```bash
helm upgrade my-release ./cloudchange-demo -n cloudchange-test
```

If the upgrade causes issues, rollback to the previous revision:
```bash
# View history
helm history my-release -n cloudchange-test

# Rollback to revision 1
helm rollback my-release 1 -n cloudchange-test
```
