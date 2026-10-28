import pytest
from app.schemas.change_detection import ChangeItem
from app.schemas.dependency_analysis import ImpactResponse, GraphData, Node, Edge
from app.modules.risk_analysis.blast_radius import BlastRadiusCalculator
from app.modules.risk_analysis.engine import RiskEngine
from app.schemas.risk_analysis import RiskRequest

def get_mock_impact(changed_resource: str, criticality: str, external_traffic: bool):
    nodes = [
        Node(id=changed_resource, label=changed_resource, type="Service", criticality=criticality)
    ]
    if external_traffic:
        nodes.append(Node(id="api-gateway", label="API Gateway", type="Gateway", criticality="high"))
        affected_apis = ["api-gateway"]
    else:
        affected_apis = []

    subgraph = GraphData(nodes=nodes, edges=[])
    
    return ImpactResponse(
        changed_resource=changed_resource,
        affected_services=[changed_resource],
        affected_deployments=[f"{changed_resource}-deployment"],
        affected_pods=[f"{changed_resource}-pod"],
        affected_apis=affected_apis,
        dependency_depth=2,
        direct_dependencies=[],
        indirect_dependencies=[],
        subgraph=subgraph
    )

def test_blast_radius_calculator():
    calc = BlastRadiusCalculator()
    impact = get_mock_impact("payment-service", "critical", True)
    
    blast = calc.calculate(impact)
    assert blast.affected_services_count == 1
    assert blast.criticality == "CRITICAL"
    assert blast.traffic_exposure == "EXTERNAL"

def test_risk_engine_low_risk():
    calc = BlastRadiusCalculator()
    engine = RiskEngine(calc)
    impact = get_mock_impact("low-service", "low", False)
    changes = [
        ChangeItem(type="MODIFIED", path="metadata.labels.env", old="dev", new="prod")
    ]
    
    res = engine.evaluate("low-service", changes, impact)
    assert res.risk_score == 0
    assert res.risk_level == "LOW"

def test_risk_engine_high_risk():
    calc = BlastRadiusCalculator()
    engine = RiskEngine(calc)
    impact = get_mock_impact("critical-service", "critical", True)
    changes = [
        ChangeItem(type="REPLICA_REDUCTION", path="spec.replicas", old=3, new=1),
        ChangeItem(type="REMOVED", path="spec.template.spec.containers[0].livenessProbe", old={"path": "/health"}, new=None)
    ]
    
    res = engine.evaluate("critical-service", changes, impact)
    
    # Replica Reduction: 20
    # Missing Probe: 15
    # High Traffic: 15
    # Critical Service: 20
    # Total: 70
    assert res.risk_score == 70
    assert res.risk_level == "HIGH"

def test_risk_engine_critical_cap():
    calc = BlastRadiusCalculator()
    engine = RiskEngine(calc)
    impact = get_mock_impact("super-service", "critical", True)
    changes = [
        ChangeItem(type="REPLICA_REDUCTION", path="spec.replicas", old=3, new=1), # 20
        ChangeItem(type="MEMORY_REDUCTION", path="resources.limits.memory", old="2Gi", new="1Gi"), # 20
        ChangeItem(type="REMOVED", path="spec.template.spec.containers[0].livenessProbe", old={"path": "/health"}, new=None), # 15
        ChangeItem(type="MODIFIED", path="securityContext.privileged", old=False, new=True) # 10
    ]
    
    res = engine.evaluate("super-service", changes, impact)
    
    # Score sum: 20+20+15+10 + 15(Traffic) + 20(Critical) = 100
    assert res.risk_score == 100
    assert res.risk_level == "CRITICAL"
