from typing import List, Set
from app.modules.dependency_analysis.graph import DependencyGraph
from app.schemas.dependency_analysis import ImpactResponse, GraphData, Node, Edge

class ImpactAnalyzer:
    def __init__(self, graph: DependencyGraph):
        self.graph = graph

    def analyze(self, changed_resource_id: str) -> ImpactResponse:
        if changed_resource_id not in self.graph.nodes:
            return self._empty_response(changed_resource_id)

        # BFS to find all dependents (nodes that depend on the changed resource)
        # This will traverse backward_edges
        direct_dependencies = list(self.graph.get_dependents(changed_resource_id))
        
        visited: Set[str] = set()
        queue = [changed_resource_id]
        visited.add(changed_resource_id)
        
        depths = {changed_resource_id: 0}
        max_depth = 0
        
        # Calculate impact by walking backwards in the dependency chain
        while queue:
            current = queue.pop(0)
            current_depth = depths[current]
            
            for dependent in self.graph.get_dependents(current):
                if dependent not in visited:
                    visited.add(dependent)
                    depths[dependent] = current_depth + 1
                    max_depth = max(max_depth, depths[dependent])
                    queue.append(dependent)
                    
        # Remove the changed resource itself from the affected set
        if changed_resource_id in visited:
            visited.remove(changed_resource_id)
            
        indirect_dependencies = [node_id for node_id in visited if node_id not in direct_dependencies]
        
        affected_services = []
        affected_apis = []
        
        for node_id in visited:
            node = self.graph.nodes[node_id]
            if node.type == "Service":
                affected_services.append(node_id)
            elif node.type in ["Ingress", "Gateway"]:
                affected_apis.append(node_id)

        # Build subgraph
        subgraph_nodes = [self.graph.nodes[changed_resource_id]] + [self.graph.nodes[n] for n in visited]
        subgraph_edges = []
        for edge in self.graph.edges:
            # We want edges that point towards the changed resource or intermediate affected nodes
            if edge.source in visited and (edge.target in visited or edge.target == changed_resource_id):
                subgraph_edges.append(edge)
                
        # Since node IDs are already Deployment names in our graph
        affected_deployments = affected_services
        affected_pods = [] # True pod counts are dynamically retrieved via k8s if necessary
        
        return ImpactResponse(
            changed_resource=changed_resource_id,
            affected_services=affected_services,
            affected_deployments=affected_deployments,
            affected_pods=affected_pods,
            affected_apis=affected_apis,
            dependency_depth=max_depth,
            direct_dependencies=direct_dependencies,
            indirect_dependencies=indirect_dependencies,
            subgraph=GraphData(nodes=subgraph_nodes, edges=subgraph_edges)
        )

    def _empty_response(self, changed_resource_id: str) -> ImpactResponse:
        return ImpactResponse(
            changed_resource=changed_resource_id,
            affected_services=[],
            affected_deployments=[],
            affected_pods=[],
            affected_apis=[],
            dependency_depth=0,
            direct_dependencies=[],
            indirect_dependencies=[],
            subgraph=GraphData(nodes=[], edges=[])
        )
