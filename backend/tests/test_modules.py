import pytest
from app.modules.change_detection.detector import ChangeDetector
from app.modules.dependency_analysis.analyzer import DependencyAnalyzer
from app.modules.dependency_analysis.impact import ImpactAnalyzer
from app.modules.risk_analysis.blast_radius import BlastRadiusCalculator
from app.modules.risk_analysis.engine import RiskEngine
from app.modules.deployment_strategy.advisor import DeploymentStrategyAdvisor
from app.schemas.dependency_analysis import ImpactResponse, GraphData
from app.schemas.deployment_strategy import RecommendationRequest
from app.modules.canary_deployment.rollback import RollbackManager
from app.schemas.change_detection import ChangeItem

def test_change_detection():
    detector = ChangeDetector()
    
    old_yaml = """
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 3
  template:
    spec:
      containers:
      - resources:
          requests:
            memory: "512Mi"
"""
    # 1. No changes
    changes = detector.compare(old_yaml, old_yaml)
    assert len(changes) == 0

    # 2. Replica reduction & Memory reduction
    new_yaml = """
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 1
  template:
    spec:
      containers:
      - resources:
          requests:
            memory: "128Mi"
"""
    changes = detector.compare(old_yaml, new_yaml)
    assert len(changes) == 2
    types = [c.type for c in changes]
    assert "REPLICA_REDUCTION" in types
    assert "MEMORY_REDUCTION" in types

def test_dependency_and_impact():
    analyzer = DependencyAnalyzer()
    graph = analyzer.get_graph()
    impact = ImpactAnalyzer(graph)
    
    # 1. Direct & Indirect
    res = impact.analyze("payment-service")
    assert "order-service" in res.affected_services
    assert "api-gateway" in res.affected_apis
    
    # 2. No dependency
    res_none = impact.analyze("unknown-service")
    assert len(res_none.affected_services) == 0

def test_blast_radius():
    calc = BlastRadiusCalculator()
    
    # Low impact — use properly formed ImpactResponse
    res = calc.calculate(ImpactResponse(
        changed_resource="test-service",
        affected_services=[],
        affected_deployments=[],
        affected_pods=[],
        affected_apis=[],
        dependency_depth=0,
        direct_dependencies=[],
        indirect_dependencies=[],
        subgraph=GraphData(nodes=[], edges=[])
    ))
    assert res.criticality == "LOW"
    
    # High impact
    from app.schemas.dependency_analysis import Node
    high_nodes = [
        Node(id="a", label="Service A", type="Service", criticality="high"),
        Node(id="b", label="Service B", type="Service", criticality="high"),
        Node(id="c", label="Service C", type="Service", criticality="critical"),
    ]
    res = calc.calculate(ImpactResponse(
        changed_resource="test-service",
        affected_services=["a", "b", "c"],
        affected_deployments=["a-deployment", "b-deployment", "c-deployment"],
        affected_pods=["a-pod-1", "b-pod-1", "c-pod-1", "a-pod-2", "b-pod-2", "c-pod-2", "a-pod-3", "b-pod-3", "c-pod-3", "c-pod-4"],
        affected_apis=["ingress", "gateway"],
        dependency_depth=3,
        direct_dependencies=["a"],
        indirect_dependencies=["b", "c"],
        subgraph=GraphData(nodes=high_nodes, edges=[])
    ))
    assert res.criticality in ["HIGH", "CRITICAL"]

def test_risk_engine():
    calc = BlastRadiusCalculator()
    engine = RiskEngine(calc)
    
    impact = ImpactResponse(
        changed_resource="test-service",
        affected_services=["api-gateway"],
        affected_deployments=["api-gateway-deployment"],
        affected_pods=["api-gateway-pod"],
        affected_apis=["api-gateway"],
        dependency_depth=1,
        direct_dependencies=["api-gateway"],
        indirect_dependencies=[],
        subgraph=GraphData(nodes=[], edges=[])
    )
    
    # Missing Probe
    change = ChangeItem(path="spec.template.spec.containers.0.livenessProbe", type="REMOVED", old="{}", new="null")
    res = engine.evaluate("test", [change], impact)
    assert any(f.factor == "Missing Probe" for f in res.risk_factors)
    
    # Security Issue
    change2 = ChangeItem(path="spec.template.spec.containers.0.securityContext.privileged", type="MODIFIED", old="false", new="true")
    res2 = engine.evaluate("test", [change2], impact)
    assert any(f.factor == "Security Issue" for f in res2.risk_factors)

def test_deployment_advisor():
    advisor = DeploymentStrategyAdvisor()
    
    # LOW
    res = advisor.recommend(RecommendationRequest(risk_score=20, risk_level="LOW", blast_radius={"dependency_depth": 1, "criticality": "LOW", "traffic_exposure": "INTERNAL", "affected_services_count": 0, "affected_pods_count": 0}, affected_services=[], criticality="LOW"))
    assert res.strategy == "ROLLING"
    
    # MEDIUM
    res = advisor.recommend(RecommendationRequest(risk_score=50, risk_level="MEDIUM", blast_radius={"dependency_depth": 1, "criticality": "MEDIUM", "traffic_exposure": "INTERNAL", "affected_services_count": 0, "affected_pods_count": 0}, affected_services=[], criticality="MEDIUM"))
    assert res.strategy == "CANARY"
    
    # CRITICAL
    res = advisor.recommend(RecommendationRequest(risk_score=95, risk_level="CRITICAL", blast_radius={"dependency_depth": 1, "criticality": "CRITICAL", "traffic_exposure": "EXTERNAL", "affected_services_count": 0, "affected_pods_count": 0}, affected_services=[], criticality="CRITICAL"))
    assert res.requires_approval == True

def test_rollback_manager():
    # In-memory tests for RollbackManager logic
    rm = RollbackManager()
    
    # Invalid
    res = rm.execute_rollback("non-existent")
    assert res.status == "NOT_FOUND"
    
    # Success
    rm.record_deployment("srv", "v1")
    rm.record_deployment("srv", "v2")
    res = rm.execute_rollback("srv")
    assert res.status == "ROLLBACK_COMPLETED"
    
    # Idempotent
    res2 = rm.execute_rollback("srv")
    assert res2.status == "ROLLBACK_COMPLETED"
