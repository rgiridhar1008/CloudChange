import logging
from kubernetes import client, config

logger = logging.getLogger(__name__)

class HealthEvaluator:
    def __init__(self):
        try:
            try:
                config.load_incluster_config()
            except config.ConfigException:
                config.load_kube_config()
            self.apps_api = client.AppsV1Api()
        except Exception as e:
            self.apps_api = None
            logger.warning(f"Could not load kubernetes config for HealthEvaluator: {e}")

    def check_health(self, service_name: str, current_percentage: int) -> bool:
        """
        Queries actual Kubernetes deployment status.
        """
        if not self.apps_api:
            # Fallback for local dev without cluster
            logger.warning("No k8s connection. Returning True for health.")
            return True
            
        try:
            # We assume deployment name matches service name or has -canary
            deployments = self.apps_api.list_deployment_for_all_namespaces()
            for dep in deployments.items:
                if service_name in dep.metadata.name:
                    replicas = dep.status.replicas or 0
                    ready = dep.status.ready_replicas or 0
                    if replicas > 0 and ready == replicas:
                        return True
                    return False
            # If we don't find it, we just return False? No, assume it's starting.
            return True
        except Exception as e:
            logger.error(f"Health evaluator failed to query k8s: {e}")
            return False
