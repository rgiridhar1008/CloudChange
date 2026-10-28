from pydantic import BaseModel
from typing import List, Optional

class MetricValue(BaseModel):
    value: float
    unit: str

class MetricsResponse(BaseModel):
    service: str
    status: str
    cpu: MetricValue
    memory: MetricValue
    latency: MetricValue
    error_rate: float
    pod_restarts: int
    readiness: float
    pods: List[str] = []
    
    # Backward compatibility
    service_name: Optional[str] = None
    cpu_usage_mcores: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    request_rate_rps: Optional[float] = None
    error_rate_percentage: Optional[float] = None
    latency_ms: Optional[float] = None
    pod_readiness_percentage: Optional[float] = None

class HealthResponse(BaseModel):
    service_name: str
    health_status: str # HEALTHY or UNHEALTHY
    failure_reasons: List[str]
    metrics: MetricsResponse
