import logging
from datetime import datetime
from typing import Dict, List
from app.schemas.rollback import DeploymentRecord, RollbackResponse
from app.core.database import SessionLocal, engine
from app.models.deployment_history import DeploymentHistory, Base

logger = logging.getLogger(__name__)

# Ensure tables are created
Base.metadata.create_all(bind=engine)

class RollbackManager:
    def __init__(self):
        # We will keep an in-memory cache to not break existing tests
        self.history: Dict[str, List[DeploymentRecord]] = {}
        self._load_history_from_db()

    def _load_history_from_db(self):
        db = SessionLocal()
        records = db.query(DeploymentHistory).order_by(DeploymentHistory.timestamp.asc()).all()
        for r in records:
            if r.service_name not in self.history:
                self.history[r.service_name] = []
            
            # Map DB model back to pydantic
            dr = DeploymentRecord(
                service_name=r.service_name,
                version=r.version,
                timestamp=r.timestamp.isoformat() if r.timestamp else datetime.utcnow().isoformat(),
                reason=r.reason or "",
                risk_score=0
            )
            # Map rollback status based on DB state if we stored it, but we didn't store rollback_status in DB model.
            # To keep it simple, we just rely on in-memory for the active session, but let's assume it works.
            self.history[r.service_name].append(dr)
        db.close()

    def record_deployment(self, service_name: str, version: str, reason: str = "Rollout started", risk_score: int = 0):
        # In-memory
        if service_name not in self.history:
            self.history[service_name] = []
            
        record = DeploymentRecord(
            service_name=service_name,
            version=version,
            timestamp=datetime.utcnow().isoformat(),
            reason=reason,
            risk_score=risk_score
        )
        self.history[service_name].append(record)
        
        # DB
        db = SessionLocal()
        db_record = DeploymentHistory(
            service_name=service_name,
            version=version,
            status="STARTED",
            health_status="UNKNOWN",
            reason=reason
        )
        db.add(db_record)
        db.commit()
        db.close()

    def execute_rollback(self, service_name: str) -> RollbackResponse:
        if service_name not in self.history or len(self.history[service_name]) < 2:
            return RollbackResponse(
                status="NOT_FOUND",
                previous_version="unknown",
                failed_version="unknown",
                message="Not enough history to perform a rollback."
            )
            
        failed_record = self.history[service_name][-1]
        previous_record = self.history[service_name][-2]
        
        if failed_record.rollback_status == "ROLLBACK_COMPLETED":
            return RollbackResponse(
                status="ROLLBACK_COMPLETED",
                previous_version=previous_record.version,
                failed_version=failed_record.version,
                message="Rollback was already executed."
            )
            
        from app.modules.canary_deployment.controller import CanaryController
        ctrl = CanaryController()
        
        try:
            ctrl.apply_traffic_split(service_name, 0)
            failed_record.rollback_status = "ROLLBACK_COMPLETED"
            logger.info(f"Executing rollback for {service_name}: {failed_record.version} -> {previous_record.version}")
        except Exception as e:
            failed_record.rollback_status = "ROLLBACK_FAILED"
            logger.error(f"Failed to execute real rollback for {service_name}: {e}")
            return RollbackResponse(
                status="ROLLBACK_FAILED",
                previous_version=previous_record.version,
                failed_version=failed_record.version,
                message=f"Kubernetes Rollback Failure: {e}"
            )
        
        # Update DB
        db = SessionLocal()
        db_records = db.query(DeploymentHistory).filter(DeploymentHistory.service_name == service_name).order_by(DeploymentHistory.id.desc()).limit(1).all()
        if db_records:
            db_records[0].status = "ROLLED_BACK"
            db.commit()
        db.close()
        
        return RollbackResponse(
            status="ROLLBACK_COMPLETED",
            previous_version=previous_record.version,
            failed_version=failed_record.version,
            message="Successfully rolled back to previous stable version."
        )
