from fastapi import APIRouter
from app.schemas.deployment_strategy import RecommendationRequest, RecommendationResponse
from app.modules.deployment_strategy.advisor import DeploymentStrategyAdvisor

from app.schemas.canary_deployment import (
    StartDeploymentRequest,
    PromoteDeploymentRequest,
    StopDeploymentRequest,
    DeploymentStatusResponse
)
from app.modules.canary_deployment.controller import CanaryController
from app.modules.canary_deployment.rollback import RollbackManager
from app.modules.canary_deployment.engine import DeploymentEngine

from app.modules.monitoring.service import MonitoringService
from app.modules.monitoring.rules import HealthEvaluatorRules

from app.modules.ai_explanation.service import AIExplanationService
from app.schemas.rollback import RollbackRequest, RollbackResponse

router = APIRouter()
advisor = DeploymentStrategyAdvisor()

# Setup Deployment Engine with Monitoring and Rollback
canary_ctrl = CanaryController()
monitoring_service = MonitoringService()
health_rules = HealthEvaluatorRules()
rollback_manager = RollbackManager()
deployment_engine = DeploymentEngine(canary_ctrl, monitoring_service, health_rules, rollback_manager)

# Setup AI Service
ai_service = AIExplanationService()

@router.post("/recommendation", response_model=RecommendationResponse)
async def get_recommendation(request: RecommendationRequest):
    """Generates a deployment strategy recommendation based on risk and blast radius."""
    response_data = advisor.recommend(request)
    
    payload = {
        "risk_score": request.risk_score,
        "risk_level": request.risk_level,
        "blast_radius": request.blast_radius,
        "affected_services": request.affected_services,
        "strategy": response_data.strategy,
        "reason": response_data.reason
    }
    
    explanation = await ai_service.get_explanation(payload)
    response_data.explanation = explanation
    
    return response_data

@router.post("/start", response_model=DeploymentStatusResponse)
async def start_deployment(request: StartDeploymentRequest):
    return await deployment_engine.start_deployment(request.service_name, request.new_version)

@router.get("/status", response_model=DeploymentStatusResponse)
async def get_deployment_status(service_name: str):
    return await deployment_engine.get_status(service_name)

@router.post("/promote", response_model=DeploymentStatusResponse)
async def promote_deployment(request: PromoteDeploymentRequest):
    return await deployment_engine.promote(request.service_name)

@router.post("/stop", response_model=DeploymentStatusResponse)
async def stop_deployment(request: StopDeploymentRequest):
    return await deployment_engine.stop(request.service_name)

@router.post("/rollback", response_model=RollbackResponse)
async def execute_rollback(request: RollbackRequest):
    return rollback_manager.execute_rollback(request.service_name)

