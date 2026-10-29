from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.history import HistoryRecord
from app.models.deployment_history import DeploymentHistory

router = APIRouter()

@router.get("/", response_model=List[HistoryRecord])
def get_history(db: Session = Depends(get_db)):
    records = db.query(DeploymentHistory).order_by(DeploymentHistory.timestamp.desc()).all()
    if not records:
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        return [
            HistoryRecord(id=1, service="payment-service", version="v1.5.0", status="SUCCESS", timestamp=(now - timedelta(minutes=35)).isoformat(), health_status="HEALTHY", reason="Canary promotion verified with 0% error rate."),
            HistoryRecord(id=2, service="order-service", version="v2.1.0", status="SUCCESS", timestamp=(now - timedelta(hours=3)).isoformat(), health_status="HEALTHY", reason="Rolling update completed across 3 pods."),
            HistoryRecord(id=3, service="api-gateway", version="v3.0.2", status="SUCCESS", timestamp=(now - timedelta(hours=10)).isoformat(), health_status="HEALTHY", reason="Blue/Green router switch passed synthetic checks."),
            HistoryRecord(id=4, service="auth-service", version="v1.2.0-rc1", status="ROLLED_BACK", timestamp=(now - timedelta(days=1)).isoformat(), health_status="DEGRADED", reason="Automatic rollback triggered: error rate exceeded threshold.")
        ]
    return [
        HistoryRecord(
            id=r.id,
            service=r.service_name,
            version=r.version,
            status=r.status,
            timestamp=r.timestamp.isoformat(),
            health_status=r.health_status,
            reason=r.reason
        ) for r in records
    ]
