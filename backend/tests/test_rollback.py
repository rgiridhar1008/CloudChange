import pytest
import asyncio
from app.modules.canary_deployment.controller import CanaryController
from app.modules.canary_deployment.rollback import RollbackManager
from app.modules.canary_deployment.engine import DeploymentEngine
from app.modules.monitoring.service import MonitoringService
from app.modules.monitoring.rules import HealthEvaluatorRules
from app.schemas.rollback import DeploymentRecord

@pytest.fixture
def engine():
    canary = CanaryController()
    monitoring = MonitoringService()
    rules = HealthEvaluatorRules()
    rollback = RollbackManager(load_db=False)
    rollback.history = {}
    
    # Pre-seed history so rollback has a "previous" version
    rollback.record_deployment("healthy-service", "v1.0")
    rollback.record_deployment("unhealthy-service", "v1.0")
    rollback.record_deployment("fail-rollback", "v1.0")
    rollback.record_deployment("unhealthy-fail-rollback", "v1.0")
    
    return DeploymentEngine(canary, monitoring, rules, rollback)

@pytest.mark.asyncio
async def test_successful_deployment(engine):
    engine.rollback_manager.history["healthy-service"] = [
        DeploymentRecord(service_name="healthy-service", version="v1.0", timestamp="2026-01-01T00:00:00", reason="init", risk_score=0)
    ]
    res = await engine.start_deployment("healthy-service", "v2.0")
    assert res.status == "IN_PROGRESS"
    assert res.health_status == "HEALTHY"
    
    # Check history recorded v2.0
    history = engine.rollback_manager.history["healthy-service"]
    assert len(history) == 2
    assert history[-1].version == "v2.0"

@pytest.mark.asyncio
async def test_failed_health_check_auto_rollback(engine):
    # 'unhealthy' in the name triggers the mock to return bad metrics
    res = await engine.start_deployment("unhealthy-service", "v2.0")
    
    # It should immediately detect unhealthy, rollback, and update status
    assert res.status == "ROLLED_BACK"
    assert res.health_status == "UNHEALTHY"
    
    # Check history
    history = engine.rollback_manager.history["unhealthy-service"]
    assert history[-1].rollback_status == "ROLLBACK_COMPLETED"

@pytest.mark.asyncio
async def test_rollback_failure(engine):
    # 'fail-rollback' triggers the simulated rollback failure
    # 'unhealthy' triggers the bad health check so rollback is attempted
    res = await engine.start_deployment("unhealthy-fail-rollback", "v2.0")
    
    # It detected unhealthy, tried to rollback, but rollback failed
    assert res.status == "ROLLED_BACK"
    assert res.health_status == "UNHEALTHY"
    
    history = engine.rollback_manager.history["unhealthy-fail-rollback"]
    assert history[-1].rollback_status == "ROLLBACK_FAILED"

@pytest.mark.asyncio
async def test_manual_rollback(engine):
    engine.rollback_manager.history["healthy-service"] = [
        DeploymentRecord(service_name="healthy-service", version="v1.0", timestamp="2026-01-01T00:00:00", reason="init", risk_score=0),
        DeploymentRecord(service_name="healthy-service", version="v2.0", timestamp="2026-01-01T00:00:00", reason="init", risk_score=0)
    ]
    # Start healthy
    res = await engine.start_deployment("healthy-service", "v3.0")
    assert res.status == "IN_PROGRESS"
    
    # Manually call rollback manager
    rollback_res = engine.rollback_manager.execute_rollback("healthy-service")
    assert rollback_res.status == "ROLLBACK_COMPLETED"
    assert rollback_res.previous_version == "v2.0"
    
    # Idempotency check: calling again returns ROLLBACK_COMPLETED safely
    rollback_res2 = engine.rollback_manager.execute_rollback("healthy-service")
    assert rollback_res2.status == "ROLLBACK_COMPLETED"
