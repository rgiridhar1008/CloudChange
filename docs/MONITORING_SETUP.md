# Monitoring Setup in Minikube

This guide explains how to integrate Prometheus and Grafana into the local Minikube environment to support CloudChange's Phase 11 Monitoring requirements.

## 1. Install Prometheus and Grafana

The easiest way to get both running is via the `kube-prometheus-stack` Helm chart.

```bash
# Add the Prometheus Community Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install the stack in the monitoring namespace
helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace
```

## 2. Accessing Grafana

Once the pods are running, you can port-forward to access Grafana locally:

```bash
kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring
```

- **URL**: `http://localhost:3000`
- **Username**: `admin`
- **Password**: `prom-operator` (default, you can retrieve it via `kubectl get secret prometheus-grafana -n monitoring -o jsonpath="{.data.admin-password}" | base64 --decode`)

## 3. Importing the Dashboard

1. Open Grafana at `http://localhost:3000`.
2. Go to **Dashboards** > **Import**.
3. Upload the `k8s/monitoring/grafana-dashboard.json` file provided in this repository.
4. Select the default Prometheus data source.
5. Click **Import**.

## 4. Connecting the Backend to Prometheus

The CloudChange backend `MonitoringService` is configured to reach Prometheus at `http://localhost:9090`. 
To ensure it works, port-forward the Prometheus server:

```bash
kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090 -n monitoring
```

If you are running the backend inside the cluster in the future, you will configure `PROMETHEUS_URL=http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090`.

*Note*: For demonstration purposes, passing `mock=True` to the `/api/v1/monitoring/health` endpoint will simulate the Prometheus queries and evaluate the rules safely without requiring the live cluster components to be fully populated with traffic.
