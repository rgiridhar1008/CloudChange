from typing import List, Dict, Set
from app.schemas.dependency_analysis import Node, Edge, GraphData

class DependencyGraph:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        # Adjacency list: node -> set of nodes it depends on
        self.forward_edges: Dict[str, Set[str]] = {}
        # Adjacency list: node -> set of nodes that depend on it
        self.backward_edges: Dict[str, Set[str]] = {}

    def add_node(self, node: Node):
        if node.id not in self.nodes:
            self.nodes[node.id] = node
            self.forward_edges[node.id] = set()
            self.backward_edges[node.id] = set()

    def add_edge(self, edge: Edge):
        if edge.source in self.nodes and edge.target in self.nodes:
            self.edges.append(edge)
            self.forward_edges[edge.source].add(edge.target)
            self.backward_edges[edge.target].add(edge.source)

    def get_graph_data(self) -> GraphData:
        return GraphData(
            nodes=list(self.nodes.values()),
            edges=self.edges
        )

    def get_dependents(self, node_id: str) -> Set[str]:
        """Returns the set of nodes that depend on the given node_id."""
        return self.backward_edges.get(node_id, set())

    def get_dependencies(self, node_id: str) -> Set[str]:
        """Returns the set of nodes that the given node_id depends on."""
        return self.forward_edges.get(node_id, set())
