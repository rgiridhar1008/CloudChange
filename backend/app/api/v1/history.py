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
