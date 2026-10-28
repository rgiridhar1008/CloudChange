import pytest
from app.modules.canary_deployment.health import HealthEvaluator
from app.modules.canary_deployment.controller import CanaryController
from app.modules.canary_deployment.engine import DeploymentEngine

def test_healthy_deployment_promotion():
    engine = DeploymentEngine(HealthEvaluator(), CanaryController())
    
    # Start
    res = engine.start_deployment("order-service", "v2.0")
    assert res.status == "IN_PROGRESS"
    assert res.current_percentage == 10
    assert res.health_status == "HEALTHY"
    
    # Promote to 25
    res = engine.promote("order-service")
    assert res.current_percentage == 25
    assert res.status == "IN_PROGRESS"
    
    # Promote to 50
    res = engine.promote("order-service")
    assert res.current_percentage == 50
    
    # Promote to 100
    res = engine.promote("order-service")
    assert res.current_percentage == 100
    assert res.status == "SUCCESS"

def test_unhealthy_deployment_blocked():
    engine = DeploymentEngine(HealthEvaluator(), CanaryController())
    
    # Start unhealthy (our mock fails if "fail" in name)
    res = engine.start_deployment("fail-service", "v2.0")
    assert res.status == "FAILED"
    assert res.health_status == "UNHEALTHY"
    
    # Try to promote
    res = engine.promote("fail-service")
    assert res.status == "FAILED"
    assert res.current_percentage == 10 # Stuck at 10%

def test_deployment_stop():
    engine = DeploymentEngine(HealthEvaluator(), CanaryController())
    
    engine.start_deployment("payment-service", "v1.1")
    engine.promote("payment-service") # Now at 25%
    
    res = engine.stop("payment-service")
    assert res.status == "PAUSED"
    assert res.current_percentage == 25
