# Kubernetes Deployment Guide (Minikube)

This guide explains how to deploy the CloudChange sample microservices application locally using Minikube.

## Prerequisites
- [Minikube](https://minikube.sigs.k8s.io/docs/start/) installed
- [kubectl](https://kubernetes.io/docs/tasks/tools/) installed
- [Docker](https://docs.docker.com/get-docker/) installed

## 1. Start Minikube

Start Minikube and enable the Ingress addon to route traffic to the frontend and API gateway.

```bash
minikube start
minikube addons enable ingress
```

## 2. Build Docker Images inside Minikube

To avoid pushing images to a public registry, we need to build them directly inside Minikube's Docker daemon.

Point your terminal to Minikube's Docker daemon:
```bash
# On Windows PowerShell
& minikube -p minikube docker-env | Invoke-Expression

# On Linux/macOS
eval $(minikube docker-env)
```

Build the images from the root of the project:
```bash
# Build Backend Services
docker build -t cloudchange-user-service:latest ./services/sample-app/user-service
docker build -t cloudchange-payment-service:latest ./services/sample-app/payment-service
docker build -t cloudchange-order-service:latest ./services/sample-app/order-service
docker build -t cloudchange-api-gateway:latest ./services/sample-app/api-gateway

# Build Frontend
docker build -t cloudchange-frontend:latest ./services/sample-app/frontend
```

## 3. Deploy Kubernetes Manifests

Apply the manifests in the correct order.

```bash
# 1. Create the namespace
kubectl apply -f k8s/namespace.yaml

# 2. Create configmaps and secrets
kubectl apply -f k8s/configmaps/
kubectl apply -f k8s/secrets/

# 3. Create services
kubectl apply -f k8s/services/

# 4. Create deployments
kubectl apply -f k8s/deployments/

# 5. Create Ingress
kubectl apply -f k8s/ingress.yaml
```

## 4. Verify Deployment

Wait for all pods to become `Running` and `Ready`:
```bash
kubectl get pods -n cloudchange-test -w
```

Check the services:
```bash
kubectl get services -n cloudchange-test
```

## 5. Access the Application

Since we are using Minikube with Ingress, you can access the frontend via the Minikube IP:

```bash
minikube ip
```

Navigate to `http://<MINIKUBE_IP>` in your browser to access the E-commerce UI and test the checkout flow.
