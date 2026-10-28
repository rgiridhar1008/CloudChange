from fastapi import APIRouter
from app.schemas.monitoring import MetricsResponse, HealthResponse
from app.modules.monitoring.service import MonitoringService
from app.modules.monitoring.rules import HealthEvaluatorRules

router = APIRouter()
monitoring_service = MonitoringService()
health_rules = HealthEvaluatorRules()

@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(service_name: str):
    """Fetches current monitoring metrics for a service."""
    metrics = await monitoring_service.get_metrics(service_name)
    return metrics

@router.get("/health", response_model=HealthResponse)
async def get_health(service_name: str):
    """Evaluates metrics against health rules to determine deployment health."""
    metrics = await monitoring_service.get_metrics(service_name)
    return health_rules.evaluate(metrics)
