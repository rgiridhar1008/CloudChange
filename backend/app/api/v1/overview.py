from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import os
from app.core.database import get_db
from app.schemas.overview import OverviewResponse, ClusterStatus, CurrentDeployment, TrafficSplit
from app.models.deployment_history import DeploymentHistory
from app.api.v1.deployment import deployment_engine
from app.api.v1.cluster import get_cluster_health

router = APIRouter()

@router.get("/", response_model=OverviewResponse)
def get_overview(db: Session = Depends(get_db)):
    # 1. Cluster status
    health_data = get_cluster_health()
    cluster = ClusterStatus(name=health_data.cluster, status=health_data.status)
    
    # 2. Database stats
    active_deployments = 0
    records = db.query(DeploymentHistory).all()
    
    total_risk = sum((getattr(r, 'risk_score', 0) or 0) for r in records if getattr(r, 'risk_score', None) is not None)
    count = len([r for r in records if getattr(r, 'risk_score', None) is not None])
    average_risk_score = int(total_risk / count) if count > 0 else 0
    
    # 3. Detect changes (0 for now, as we don't store uncommitted changes in DB natively)
    detected_changes = 0
    
    # 4. Current Deployment
    active_service = None
    active_status = None
    for service, state in deployment_engine.active_deployments.items():
        if getattr(state, "status", None) in ["IN_PROGRESS", "PAUSED", "STARTING"]:
            active_service = service
            active_status = state
            break
            
    current_deployment = None
    if active_service and active_status:
        active_deployments = 1
        current_pct = getattr(active_status, "percentage", getattr(active_status, "current_percentage", 0))
        current_deployment = CurrentDeployment(
            service=active_service,
            current_version="v1",
            target_version="v2",
            strategy="CANARY",
            traffic=TrafficSplit(stable=100-current_pct, canary=current_pct),
            status=getattr(active_status, "status", "IN_PROGRESS"),
            health=getattr(active_status, "health_status", "UNKNOWN")
        )

    in_cloud = bool(os.getenv("RENDER") or os.getenv("VERCEL") or os.getenv("DEMO_MODE", "true").lower() in ("true", "1"))
    if not current_deployment and in_cloud:
        active_deployments = 1
        average_risk_score = average_risk_score or 34
        detected_changes = 2
        current_deployment = CurrentDeployment(
            service="payment-service",
            current_version="v1.4.2",
            target_version="v1.5.0",
            strategy="CANARY",
            traffic=TrafficSplit(stable=75, canary=25),
            status="IN_PROGRESS",
            health="HEALTHY"
        )
        
    return OverviewResponse(
        cluster=cluster,
        active_deployments=active_deployments,
        average_risk_score=average_risk_score,
        detected_changes=detected_changes,
        current_deployment=current_deployment
    )
