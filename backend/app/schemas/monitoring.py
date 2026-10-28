from pydantic import BaseModel, model_validator
from typing import List, Optional, Any

class MetricValue(BaseModel):
    value: float
    unit: str

class MetricsResponse(BaseModel):
    service: str = ""
    status: str = "HEALTHY"
    cpu: MetricValue = MetricValue(value=0.0, unit="m")
    memory: MetricValue = MetricValue(value=0.0, unit="MB")
    latency: MetricValue = MetricValue(value=0.0, unit="ms")
    error_rate: float = 0.0
    pod_restarts: int = 0
    readiness: float = 100.0
    pods: List[str] = []
    
    # Backward compatibility
    service_name: Optional[str] = None
    cpu_usage_mcores: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    request_rate_rps: Optional[float] = None
    error_rate_percentage: Optional[float] = None
    latency_ms: Optional[float] = None
    pod_readiness_percentage: Optional[float] = None

    @model_validator(mode="before")
    @classmethod
    def populate_compat_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "service" not in data and "service_name" in data:
                data["service"] = data["service_name"]
            if "cpu" not in data and "cpu_usage_mcores" in data:
                data["cpu"] = MetricValue(value=float(data["cpu_usage_mcores"]), unit="m")
            if "memory" not in data and "memory_usage_mb" in data:
                data["memory"] = MetricValue(value=float(data["memory_usage_mb"]), unit="MB")
            if "latency" not in data and "latency_ms" in data:
                data["latency"] = MetricValue(value=float(data["latency_ms"]), unit="ms")
            if "error_rate" not in data and "error_rate_percentage" in data:
                data["error_rate"] = float(data["error_rate_percentage"])
            if "readiness" not in data and "pod_readiness_percentage" in data:
                data["readiness"] = float(data["pod_readiness_percentage"])
        return data

class HealthResponse(BaseModel):
    service_name: str
    health_status: str # HEALTHY or UNHEALTHY
    failure_reasons: List[str]
    metrics: MetricsResponse
