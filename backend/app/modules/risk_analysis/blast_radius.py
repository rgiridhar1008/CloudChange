from app.schemas.dependency_analysis import ImpactResponse
from app.schemas.risk_analysis import BlastRadius

class BlastRadiusCalculator:
    def __init__(self):
        pass

    def calculate(self, impact: ImpactResponse) -> BlastRadius:
        affected_services_count = len(impact.affected_services)
        affected_pods_count = len(impact.affected_pods)
        dependency_depth = impact.dependency_depth
        
        # Determine criticality based on subgraph
        criticality = "low"
        critical_levels = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        max_crit = 1
        
        for node in impact.subgraph.nodes:
            crit = node.criticality.lower()
            val = critical_levels.get(crit, 1)
            if val > max_crit:
                max_crit = val
                criticality = crit
        
        # Determine traffic exposure (if Ingress or Gateway is affected)
        traffic_exposure = "internal"
        for api in impact.affected_apis:
            traffic_exposure = "external"
            break
            
        return BlastRadius(
            affected_services_count=affected_services_count,
            affected_pods_count=affected_pods_count,
            dependency_depth=dependency_depth,
            criticality=criticality.upper(),
            traffic_exposure=traffic_exposure.upper()
        )
