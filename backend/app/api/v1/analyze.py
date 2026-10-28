from fastapi import APIRouter
from app.schemas.change_detection import ChangeRequest, ChangeResponse
from app.modules.change_detection.detector import ChangeDetector
from app.schemas.dependency_analysis import ImpactRequest, ImpactResponse, GraphData
from app.modules.dependency_analysis.analyzer import DependencyAnalyzer
from app.modules.dependency_analysis.impact import ImpactAnalyzer
from app.schemas.risk_analysis import RiskRequest, RiskResponse
from app.modules.risk_analysis.blast_radius import BlastRadiusCalculator
from app.modules.risk_analysis.engine import RiskEngine

router = APIRouter()
detector = ChangeDetector()

# Dependency Analysis instances
dependency_analyzer = DependencyAnalyzer()
# For phase 6, we initialize with the mock graph
graph = dependency_analyzer.get_graph()
impact_analyzer = ImpactAnalyzer(graph)

# Risk Analysis instances
blast_calculator = BlastRadiusCalculator()
risk_engine = RiskEngine(blast_calculator)


@router.post("/analyze/change", response_model=ChangeResponse)
async def analyze_change(request: ChangeRequest):
    changes = detector.compare(request.old_config, request.new_config)
    return ChangeResponse(changes=changes)

@router.post("/analyze/dependencies", response_model=GraphData)
async def analyze_dependencies():
    """Builds and returns the dependency graph."""
    # In a real app, this might take resources as input to build the graph
    graph = dependency_analyzer.get_graph()
    return graph.get_graph_data()

@router.post("/analyze/impact", response_model=ImpactResponse)
async def analyze_impact(request: ImpactRequest):
    """Calculates the impact of a changed resource."""
    response = impact_analyzer.analyze(request.changed_resource)
    return response

@router.get("/graph", response_model=GraphData)
async def get_graph():
    """Returns the current dependency graph data."""
    return dependency_analyzer.get_graph().get_graph_data()

@router.get("/dependencies/{service}", response_model=GraphData)
async def get_service_dependencies(service: str):
    """Returns the subgraph of dependencies for a specific service."""
    impact = impact_analyzer.analyze(service)
    return impact.subgraph

@router.post("/analyze/risk", response_model=RiskResponse)
@router.post("/risk/analyze", response_model=RiskResponse)
async def analyze_risk(request: RiskRequest):
    """Calculates the overall risk and blast radius of the changes."""
    # Calculate impact for the changed resource
    impact = impact_analyzer.analyze(request.changed_resource)
    
    # Evaluate risk based on changes and impact
    response = risk_engine.evaluate(request.changed_resource, request.changes, impact)
    return response

from app.modules.orchestration.service import OrchestratorService
from pydantic import BaseModel

orchestrator = OrchestratorService()

from typing import Optional

class UnifiedAnalyzeRequest(BaseModel):
    manifest_content: str
    old_manifest_content: Optional[str] = ""
    resource_name: str

@router.post("/analyze/unified")
async def unified_analyze(request: UnifiedAnalyzeRequest):
    """
    Executes the complete CloudChange analysis pipeline end-to-end.
    """
    result = await orchestrator.analyze_change_pipeline(request.manifest_content, request.resource_name, request.old_manifest_content)
    return result
