import pytest
from app.schemas.monitoring import MetricsResponse
from app.modules.monitoring.rules import HealthEvaluatorRules

def test_healthy_metrics():
    rules = HealthEvaluatorRules()
    
    metrics = MetricsResponse(
        service_name="payment-service",
        cpu_usage_mcores=100.0,
        memory_usage_mb=128.0,
        request_rate_rps=20.0,
        error_rate_percentage=1.0,
        latency_ms=200.0,
        pod_restarts=0,
        pod_readiness_percentage=100.0
    )
    
    res = rules.evaluate(metrics)
    assert res.health_status == "HEALTHY"
    assert len(res.failure_reasons) == 0

def test_unhealthy_error_rate():
    rules = HealthEvaluatorRules()
    
    metrics = MetricsResponse(
        service_name="payment-service",
        cpu_usage_mcores=100.0,
        memory_usage_mb=128.0,
        request_rate_rps=20.0,
        error_rate_percentage=10.0, # Threshold is 5%
        latency_ms=200.0,
        pod_restarts=0,
        pod_readiness_percentage=100.0
    )
    
    res = rules.evaluate(metrics)
    assert res.health_status == "UNHEALTHY"
    assert "Error rate 10.0% exceeds threshold of 5.0%" in res.failure_reasons

def test_unhealthy_latency_and_restarts():
    rules = HealthEvaluatorRules()
    
    metrics = MetricsResponse(
        service_name="payment-service",
        cpu_usage_mcores=100.0,
        memory_usage_mb=128.0,
        request_rate_rps=20.0,
        error_rate_percentage=0.0,
        latency_ms=800.0, # Threshold 500
        pod_restarts=3, # Threshold 2
        pod_readiness_percentage=100.0
    )
    
    res = rules.evaluate(metrics)
    assert res.health_status == "UNHEALTHY"
    assert len(res.failure_reasons) == 2
    assert "Latency 800.0ms exceeds threshold of 500.0ms" in res.failure_reasons
    assert "Pod restarts 3 exceeds threshold of 2" in res.failure_reasons

def test_unhealthy_readiness():
    rules = HealthEvaluatorRules()
    
    metrics = MetricsResponse(
        service_name="payment-service",
        cpu_usage_mcores=100.0,
        memory_usage_mb=128.0,
        request_rate_rps=20.0,
        error_rate_percentage=0.0,
        latency_ms=100.0, 
        pod_restarts=0, 
        pod_readiness_percentage=50.0 # Threshold 100
    )
    
    res = rules.evaluate(metrics)
    assert res.health_status == "UNHEALTHY"
    assert "Pod readiness is at 50.0%, expected 100.0%" in res.failure_reasons
