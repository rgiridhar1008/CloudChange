from app.schemas.monitoring import MetricsResponse, HealthResponse

class HealthEvaluatorRules:
    def __init__(self):
        # Thresholds
        self.max_error_rate = 5.0 # 5%
        self.max_latency_ms = 500.0 # 500ms
        self.min_readiness = 100.0 # 100%
        self.max_restarts = 2
        
    def evaluate(self, metrics: MetricsResponse) -> HealthResponse:
        failure_reasons = []
        
        if metrics.error_rate > self.max_error_rate:
            failure_reasons.append(f"Error rate {metrics.error_rate}% exceeds threshold of {self.max_error_rate}%")
            
        if metrics.latency.value > self.max_latency_ms:
            failure_reasons.append(f"Latency {metrics.latency.value}ms exceeds threshold of {self.max_latency_ms}ms")
            
        if metrics.readiness < self.min_readiness:
            failure_reasons.append(f"Pod readiness is at {metrics.readiness}%, expected {self.min_readiness}%")
            
        if metrics.pod_restarts > self.max_restarts:
            failure_reasons.append(f"Pod restarts {metrics.pod_restarts} exceeds threshold of {self.max_restarts}")
            
        status = "UNHEALTHY" if failure_reasons else "HEALTHY"
        
        return HealthResponse(
            service_name=metrics.service,
            health_status=status,
            failure_reasons=failure_reasons,
            metrics=metrics
        )
