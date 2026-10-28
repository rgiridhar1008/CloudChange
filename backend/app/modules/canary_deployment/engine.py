from typing import Dict, Tuple
from app.schemas.canary_deployment import DeploymentStatusResponse
from app.modules.canary_deployment.controller import CanaryController
from app.modules.canary_deployment.rollback import RollbackManager
from app.modules.monitoring.service import MonitoringService
from app.modules.monitoring.rules import HealthEvaluatorRules

class DeploymentState:
    def __init__(self, service_name: str, version: str, percentage: int):
        self.service_name = service_name
        self.version = version
        self.percentage = percentage
        self.status = "IN_PROGRESS"
        self.health_status = "UNKNOWN"
        self.message = "Deployment started"
        self.strategy = "CANARY"
        self.events = []
        
    def add_event(self, event: str, status: str):
        from datetime import datetime, timezone
        self.events.append({
            "event": event,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status
        })

class DeploymentEngine:
    def __init__(self, 
                 canary_controller: CanaryController, 
                 monitoring_service: MonitoringService, 
                 health_rules: HealthEvaluatorRules,
                 rollback_manager: RollbackManager):
        self.canary_controller = canary_controller
        self.monitoring_service = monitoring_service
        self.health_rules = health_rules
        self.rollback_manager = rollback_manager
        self.active_deployments: Dict[str, DeploymentState] = {}

    async def start_deployment(self, service_name: str, version: str) -> DeploymentStatusResponse:
        from app.modules.notifications.service import NotificationService
        # Record the start of this version
        self.rollback_manager.record_deployment(service_name, version)
        
        initial_percentage = self.canary_controller.get_initial_percentage()
        state = DeploymentState(service_name, version, initial_percentage)
        self.canary_controller.apply_traffic_split(service_name, initial_percentage)
        
        NotificationService.create_notification(f"Deployment started for {service_name} at {initial_percentage}% canary.", "INFO")
        
        # Check initial health
        healthy, message = await self._check_health(service_name)
        if healthy:
            state.health_status = "HEALTHY"
            state.add_event("DEPLOYMENT_STARTED", "SUCCESS")
        else:
            state.health_status = "UNHEALTHY"
            state.status = "ROLLED_BACK"
            state.message = f"Initial health check failed: {message}. Rolling back."
            state.add_event("DEPLOYMENT_FAILED", "FAILED")
            self.rollback_manager.execute_rollback(service_name)
            NotificationService.create_notification(f"Deployment {service_name} rolled back: {message}", "ERROR")
            
        self.active_deployments[service_name] = state
        return self._build_response(state)

    async def get_status(self, service_name: str) -> DeploymentStatusResponse:
        from app.schemas.canary_deployment import TrafficSplit
        from app.modules.notifications.service import NotificationService
        if service_name not in self.active_deployments:
            return DeploymentStatusResponse(
                service=service_name,
                status="NOT_FOUND",
                strategy="CANARY",
                current_version="v1",
                target_version="v2",
                traffic=TrafficSplit(stable=100, canary=0),
                health="UNKNOWN",
                events=[],
                service_name=service_name,
                current_percentage=0,
                health_status="UNKNOWN",
                message="No active deployment found."
            )
        state = self.active_deployments[service_name]
        
        # Re-evaluate health on status check if still in progress
        if state.status == "IN_PROGRESS":
            healthy, message = await self._check_health(service_name)
            if not healthy:
                state.health_status = "UNHEALTHY"
                state.status = "ROLLED_BACK"
                state.message = f"Health check failed during monitoring: {message}. Rolling back."
                state.add_event("HEALTH_CHECK_FAILED", "FAILED")
                self.rollback_manager.execute_rollback(service_name)
                NotificationService.create_notification(f"Deployment {service_name} rolled back: {message}", "ERROR")
            else:
                state.health_status = "HEALTHY"
                
        return self._build_response(state)

    async def promote(self, service_name: str) -> DeploymentStatusResponse:
        from app.modules.notifications.service import NotificationService
        if service_name not in self.active_deployments:
            return await self.get_status(service_name)
            
        state = self.active_deployments[service_name]
        
        if state.status in ["ROLLED_BACK", "SUCCESS", "PAUSED", "FAILED"]:
            return self._build_response(state)
            
        healthy, message = await self._check_health(service_name)
        if not healthy:
            state.health_status = "UNHEALTHY"
            state.status = "ROLLED_BACK"
            state.message = f"Cannot promote: {message}. Rolling back."
            state.add_event("PROMOTE_FAILED", "FAILED")
            self.rollback_manager.execute_rollback(service_name)
            NotificationService.create_notification(f"Promotion failed for {service_name}: {message}", "ERROR")
            return self._build_response(state)
            
        next_percentage = self.canary_controller.get_next_percentage(state.percentage)
        state.percentage = next_percentage
        self.canary_controller.apply_traffic_split(service_name, next_percentage)
        
        if next_percentage == 100:
            state.status = "SUCCESS"
            state.message = "Deployment fully rolled out to 100%."
            state.add_event("FULLY_ROLLED_OUT", "SUCCESS")
            NotificationService.create_notification(f"Deployment {service_name} fully rolled out to 100%.", "SUCCESS")
        else:
            state.message = f"Promoted to {next_percentage}%."
            state.add_event(f"PROMOTED_TO_{next_percentage}%", "SUCCESS")
            NotificationService.create_notification(f"Deployment {service_name} promoted to {next_percentage}%.", "INFO")
            
        return self._build_response(state)

    async def stop(self, service_name: str) -> DeploymentStatusResponse:
        if service_name in self.active_deployments:
            state = self.active_deployments[service_name]
            if state.status == "IN_PROGRESS":
                state.status = "PAUSED"
                state.message = "Deployment manually stopped."
                state.add_event("DEPLOYMENT_PAUSED", "WARNING")
            return self._build_response(state)
        return await self.get_status(service_name)

    async def _check_health(self, service_name: str) -> Tuple[bool, str]:
        metrics = await self.monitoring_service.get_metrics(service_name)
        health_resp = self.health_rules.evaluate(metrics)
        if health_resp.health_status == "UNHEALTHY":
            return False, ", ".join(health_resp.failure_reasons)
        return True, ""

    def _build_response(self, state: DeploymentState) -> DeploymentStatusResponse:
        from app.schemas.canary_deployment import TrafficSplit, DeploymentEvent
        events = [DeploymentEvent(**e) for e in state.events]
        return DeploymentStatusResponse(
            service=state.service_name,
            status=state.status,
            strategy=state.strategy,
            current_version="v1", # Usually derived from cluster state
            target_version=state.version,
            traffic=TrafficSplit(stable=100 - state.percentage, canary=state.percentage),
            health=state.health_status,
            events=events,
            
            # Legacy fields for backward compatibility during transition
            service_name=state.service_name,
            current_percentage=state.percentage,
            health_status=state.health_status,
            message=state.message
        )
