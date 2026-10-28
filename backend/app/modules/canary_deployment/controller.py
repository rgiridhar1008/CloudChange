import logging
from kubernetes import client, config
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)

class CanaryController:
    def __init__(self):
        # 10% -> 25% -> 50% -> 100%
        self.promotion_steps = [10, 25, 50, 100]
        try:
            config.load_incluster_config()
        except config.ConfigException:
            try:
                config.load_kube_config()
            except config.ConfigException:
                logger.warning("Could not configure kubernetes python client")
                
        # Initialize APIs. Will fail gracefully if client is not configured
        try:
            self.apps_v1 = client.AppsV1Api()
            self.custom_api = client.CustomObjectsApi()
        except Exception:
            self.apps_v1 = None
            self.custom_api = None

    def get_initial_percentage(self) -> int:
        return self.promotion_steps[0]

    def get_next_percentage(self, current: int) -> int:
        for step in self.promotion_steps:
            if step > current:
                return step
        return 100
        
    def apply_traffic_split(self, service_name: str, percentage: int):
        """
        Applies a traffic split in Kubernetes.
        Attempts to patch an Istio VirtualService first. 
        If Istio is not present, it attempts to scale a canary deployment.
        """
        logger.info(f"Applying traffic split for {service_name}: {percentage}% to new version.")
        
        if not self.apps_v1 or not self.custom_api:
            logger.error("Kubernetes client not initialized. Cannot apply traffic split.")
            return

        namespace = "default"  # Can be configured via env
        
        # 1. Try patching Istio VirtualService
        try:
            vs = self.custom_api.get_namespaced_custom_object(
                group="networking.istio.io",
                version="v1alpha3",
                namespace=namespace,
                plural="virtualservices",
                name=service_name
            )
            
            # Assuming standard 2 route setup
            vs['spec']['http'][0]['route'][0]['weight'] = 100 - percentage
            vs['spec']['http'][0]['route'][1]['weight'] = percentage
            
            self.custom_api.patch_namespaced_custom_object(
                group="networking.istio.io",
                version="v1alpha3",
                namespace=namespace,
                plural="virtualservices",
                name=service_name,
                body=vs
            )
            logger.info(f"Successfully patched Istio VirtualService for {service_name}")
            return
        except ApiException as e:
            if e.status != 404:
                logger.warning(f"Failed to patch Istio VirtualService: {e}")
            # Fall back to deployment scaling if VS not found
        except Exception as e:
            logger.warning(f"Error accessing Istio VirtualService: {e}")
            
        # 2. Try scaling Deployments (Primary vs Canary)
        try:
            # Simple assumption: 10 replicas total.
            canary_replicas = max(1, int(10 * (percentage / 100.0)))
            primary_replicas = 10 - canary_replicas
            
            if percentage == 0:
                canary_replicas = 0
                primary_replicas = 10
            elif percentage == 100:
                canary_replicas = 10
                primary_replicas = 0
                
            self._patch_deployment_replicas(f"{service_name}", primary_replicas, namespace)
            self._patch_deployment_replicas(f"{service_name}-canary", canary_replicas, namespace)
            
            logger.info(f"Scaled deployments for {service_name}: primary={primary_replicas}, canary={canary_replicas}")
        except Exception as e:
            logger.error(f"Failed to scale deployments for {service_name}: {e}")

    def _patch_deployment_replicas(self, name: str, replicas: int, namespace: str):
        try:
            body = {'spec': {'replicas': replicas}}
            self.apps_v1.patch_namespaced_deployment(name=name, namespace=namespace, body=body)
        except ApiException as e:
            if e.status != 404:
                raise e
            logger.warning(f"Deployment {name} not found in namespace {namespace}")
