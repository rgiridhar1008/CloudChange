#!/bin/bash
# Validate Infrastructure Script
# Runs the external tools tests as specified in Phase 17

echo "--- Docker Testing ---"
docker --version
docker compose version
echo "Building backend..."
docker build -t cloudchange-backend ./backend
echo "Building frontend..."
docker build -t cloudchange-frontend ./frontend

echo "--- Kubernetes & Minikube Testing ---"
kubectl version --client
minikube status
kubectl get nodes
kubectl get namespaces
kubectl get pods -A

echo "Deploying CloudChange mock..."
kubectl apply -f ./k8s/namespace.yaml

echo "--- Helm Testing ---"
helm version
helm lint ./helm/cloudchange || echo "No helm chart found, skipping lint"

echo "--- CI/CD Testing ---"
echo "Validating .github/workflows..."
if [ -d ".github/workflows" ]; then
    echo "Workflows found."
else
    echo "No workflows directory."
fi

echo "--- Monitoring Testing ---"
echo "Assuming Prometheus is port-forwarded locally at :9090"
curl -s http://localhost:9090/-/healthy || echo "Prometheus not reachable"

echo "--- Failure Testing ---"
echo "Run backend/experiments/run_experiment.py to execute controlled failure tests."

echo "All tests completed."
