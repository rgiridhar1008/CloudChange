import pytest
from app.schemas.deployment_strategy import RecommendationRequest
from app.schemas.risk_analysis import BlastRadius
from app.modules.deployment_strategy.advisor import DeploymentStrategyAdvisor

def get_request(level: str) -> RecommendationRequest:
    return RecommendationRequest(
        risk_score=50,
        risk_level=level,
        blast_radius=BlastRadius(
            affected_services_count=1,
            affected_pods_count=1,
            dependency_depth=1,
            criticality="LOW",
            traffic_exposure="INTERNAL"
        ),
        affected_services=["test-service"],
        criticality="LOW"
    )

def test_recommend_low():
    advisor = DeploymentStrategyAdvisor()
    req = get_request("LOW")
    res = advisor.recommend(req)
    
    assert res.strategy == "ROLLING"
    assert res.initial_percentage == 100
    assert not res.requires_approval

def test_recommend_medium():
    advisor = DeploymentStrategyAdvisor()
    req = get_request("MEDIUM")
    res = advisor.recommend(req)
    
    assert res.strategy == "CANARY"
    assert res.initial_percentage == 25
    assert not res.requires_approval

def test_recommend_high():
    advisor = DeploymentStrategyAdvisor()
    req = get_request("HIGH")
    res = advisor.recommend(req)
    
    assert res.strategy == "CANARY"
    assert res.initial_percentage == 10
    assert not res.requires_approval

def test_recommend_critical():
    advisor = DeploymentStrategyAdvisor()
    req = get_request("CRITICAL")
    res = advisor.recommend(req)
    
    assert res.strategy == "CANARY"
    assert res.requires_approval
