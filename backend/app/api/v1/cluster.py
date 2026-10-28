from fastapi import APIRouter
from datetime import datetime, timezone
from app.schemas.cluster import ClusterHealthResponse, ServiceListResponse, ServiceInfo
import logging

logger = logging.getLogger(__name__)

def _get_k8s_clients():
    """Lazily connect to Kubernetes so Minikube can start after the backend."""
    try:
        from kubernetes import client, config
        try:
            config.load_incluster_config()
        except config.ConfigException:
            config.load_kube_config()
        return client.CoreV1Api(), client.AppsV1Api()
    except Exception as e:
        logger.warning(f"Could not load kubernetes config: {e}")
        return None, None

router = APIRouter()

@router.get("/health", response_model=ClusterHealthResponse)
def get_cluster_health():
    core_api, _ = _get_k8s_clients()
    if not core_api:
        return ClusterHealthResponse(
            cluster="unknown",
            status="DISCONNECTED",
            nodes=0,
            ready_nodes=0,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
    try:
        nodes = core_api.list_node(_request_timeout=2)
        total_nodes = len(nodes.items)
        ready_nodes = 0
        for node in nodes.items:
            for condition in node.status.conditions:
                if condition.type == "Ready" and condition.status == "True":
                    ready_nodes += 1
                    break
        
        status = "HEALTHY" if ready_nodes > 0 else "UNHEALTHY"
        
        return ClusterHealthResponse(
            cluster="kubernetes",
            status=status,
            nodes=total_nodes,
            ready_nodes=ready_nodes,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    except Exception as e:
        logger.error(f"Failed to fetch cluster health: {e}")
        return ClusterHealthResponse(
            cluster="unknown",
            status="DISCONNECTED",
            nodes=0,
            ready_nodes=0,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

@router.get("/services", response_model=ServiceListResponse)
def get_services():
    """Returns a list of actual Kubernetes deployments."""
    _, apps_api = _get_k8s_clients()
    if not apps_api:
        return ServiceListResponse(services=[])
        
    try:
        deployments = apps_api.list_deployment_for_all_namespaces(_request_timeout=2)
        services = []
        for dep in deployments.items:
            namespace = dep.metadata.namespace
            # Ignore core kube system namespaces to focus on workloads
            if namespace in ['kube-system', 'kubernetes-dashboard', 'local-path-storage']:
                continue
                
            name = dep.metadata.name
            replicas = dep.status.replicas or 0
            ready_replicas = dep.status.ready_replicas or 0
            status = "HEALTHY" if ready_replicas >= replicas and replicas > 0 else "DEGRADED"
            
            services.append(ServiceInfo(
                name=name,
                namespace=namespace,
                type="Deployment",
                status=status,
                replicas=replicas,
                ready_replicas=ready_replicas
            ))
        return ServiceListResponse(services=services)
    except Exception as e:
        logger.error(f"Failed to fetch services: {e}")
        return ServiceListResponse(services=[])
