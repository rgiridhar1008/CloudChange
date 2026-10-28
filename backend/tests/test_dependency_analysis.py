import pytest
from app.modules.dependency_analysis.graph import DependencyGraph
from app.modules.dependency_analysis.analyzer import DependencyAnalyzer
from app.modules.dependency_analysis.impact import ImpactAnalyzer
from app.schemas.dependency_analysis import Node, Edge

def test_dependency_graph():
    graph = DependencyGraph()
    node1 = Node(id="A", label="Service A", type="Service")
    node2 = Node(id="B", label="Service B", type="Service")
    
    graph.add_node(node1)
    graph.add_node(node2)
    
    edge = Edge(source="A", target="B")
    graph.add_edge(edge)
    
    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1
    
    # A depends on B
    assert "B" in graph.get_dependencies("A")
    # B is dependent on by A
    assert "A" in graph.get_dependents("B")

def test_dependency_analyzer():
    analyzer = DependencyAnalyzer()
    graph = analyzer.get_graph()
    
    assert "ingress" in graph.nodes
    assert "api-gateway" in graph.nodes
    assert "order-service" in graph.nodes
    assert "payment-service" in graph.nodes
    assert "database" in graph.nodes
    
    # ingress -> api-gateway -> order-service -> payment-service -> database
    assert "payment-service" in graph.get_dependencies("order-service")
    assert "order-service" in graph.get_dependents("payment-service")

def test_impact_analyzer():
    analyzer = DependencyAnalyzer()
    graph = analyzer.get_graph()
    impact_analyzer = ImpactAnalyzer(graph)
    
    # If payment-service changes, who is impacted?
    # order-service -> payment-service, so order-service is impacted
    # api-gateway -> order-service, so api-gateway is impacted
    # ingress -> api-gateway, so ingress is impacted
    
    response = impact_analyzer.analyze("payment-service")
    
    assert response.changed_resource == "payment-service"
    assert "order-service" in response.direct_dependencies
    
    assert "api-gateway" in response.indirect_dependencies
    assert "ingress" in response.indirect_dependencies
    
    # payment-service shouldn't be in the affected services (it is the changed one)
    assert "order-service" in response.affected_services
    assert "payment-service" not in response.affected_services
    
    assert "api-gateway" in response.affected_apis
    assert "ingress" in response.affected_apis
    
    assert response.dependency_depth == 3  # payment (0) <- order (1) <- gateway (2) <- ingress (3)
