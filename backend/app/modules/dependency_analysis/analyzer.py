import logging
import socket
from urllib.parse import urlparse
from kubernetes import client, config
from app.modules.dependency_analysis.graph import DependencyGraph
from app.schemas.dependency_analysis import Node, Edge

logger = logging.getLogger(__name__)

def _is_host_reachable(url_str: str, timeout: float = 0.25) -> bool:
    try:
        parsed = urlparse(url_str)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False

class DependencyAnalyzer:
    def __init__(self):
        self.graph = DependencyGraph()

    def _connect_k8s(self):
        """Lazily connect to Kubernetes with fast socket check."""
        try:
            try:
                config.load_incluster_config()
            except config.ConfigException:
                config.load_kube_config()
            host = client.Configuration.get_default_copy().host
            if not _is_host_reachable(host, timeout=0.25):
                return None, None
            return client.AppsV1Api(), client.CoreV1Api()
        except Exception as e:
            logger.debug(f"Could not load kubernetes config for DependencyAnalyzer: {e}")
            return None, None

    def _build_default_graph(self):
        """Constructs the baseline microservice architecture when live K8s is not available."""
        nodes = [
            Node(id="ingress", label="ingress", type="Ingress", criticality="high"),
            Node(id="api-gateway", label="api-gateway", type="Gateway", criticality="high"),
            Node(id="order-service", label="order-service", type="Service", criticality="medium"),
            Node(id="payment-service", label="payment-service", type="Service", criticality="critical"),
            Node(id="database", label="database", type="Database", criticality="critical"),
            Node(id="user-service", label="user-service", type="Service", criticality="medium"),
        ]
        for node in nodes:
            self.graph.add_node(node)
            
        edges = [
            Edge(id="ingress-to-api-gateway", source="ingress", target="api-gateway", relationship="routes_to"),
            Edge(id="api-gateway-to-order-service", source="api-gateway", target="order-service", relationship="depends_on"),
            Edge(id="order-service-to-payment-service", source="order-service", target="payment-service", relationship="depends_on"),
            Edge(id="payment-service-to-database", source="payment-service", target="database", relationship="depends_on"),
            Edge(id="api-gateway-to-user-service", source="api-gateway", target="user-service", relationship="depends_on"),
        ]
        for edge in edges:
            self.graph.add_edge(edge)

    def build_k8s_graph(self):
        """
        Builds a graph based on baseline microservices, enriched with live Kubernetes resources.
        """
        self._build_default_graph()

        apps_v1, core_v1 = self._connect_k8s()
        if not apps_v1 or not core_v1:
            return self.graph
            
        try:
            deployments = apps_v1.list_deployment_for_all_namespaces(_request_timeout=1)
            if deployments and deployments.items:
                for dep in deployments.items:
                    namespace = dep.metadata.namespace
                    if namespace in ['kube-system', 'kubernetes-dashboard', 'local-path-storage']:
                        continue
                    name = dep.metadata.name
                    if name not in self.graph.nodes:
                        node = Node(
                            id=name, 
                            label=name, 
                            type="Service", 
                            criticality="medium",
                            namespace=namespace
                        )
                        self.graph.add_node(node)
                        
                for dep in deployments.items:
                    namespace = dep.metadata.namespace
                    if namespace in ['kube-system', 'kubernetes-dashboard', 'local-path-storage']:
                        continue
                    source_name = dep.metadata.name
                    containers = dep.spec.template.spec.containers
                    for container in containers:
                        if not container.env:
                            continue
                        for env in container.env:
                            if env.value:
                                for target_node in self.graph.nodes.values():
                                    if target_node.id != source_name and target_node.id in env.value:
                                        edge = Edge(
                                            id=f"{source_name}-to-{target_node.id}",
                                            source=source_name,
                                            target=target_node.id,
                                            relationship="depends_on"
                                        )
                                        self.graph.add_edge(edge)
        except Exception as e:
            logger.debug(f"Optional k8s workload enrichment skipped: {e}")

        return self.graph

    def get_graph(self) -> DependencyGraph:
        if not self.graph.nodes:
            self.build_k8s_graph()
        return self.graph
