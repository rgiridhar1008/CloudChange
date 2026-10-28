from pydantic import BaseModel, Field
from typing import List, Optional, Set

class Node(BaseModel):
    id: str
    label: str
    type: str  # Ingress, Gateway, Service, Database
    namespace: str = "default"
    criticality: str = "medium"

class Edge(BaseModel):
    source: str
    target: str
    type: str = "direct"

class GraphData(BaseModel):
    nodes: List[Node]
    edges: List[Edge]

class ImpactRequest(BaseModel):
    changed_resource: str

class ImpactResponse(BaseModel):
    changed_resource: str
    affected_services: List[str]
    affected_deployments: List[str]
    affected_pods: List[str]
    affected_apis: List[str]
    dependency_depth: int
    direct_dependencies: List[str]
    indirect_dependencies: List[str]
    subgraph: GraphData
