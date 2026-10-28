from pydantic import BaseModel
from typing import Optional

class RollbackRequest(BaseModel):
    service_name: str

class RollbackResponse(BaseModel):
    status: str # ROLLBACK_COMPLETED, ROLLBACK_FAILED, NOT_FOUND
    previous_version: str
    failed_version: str
    message: Optional[str] = None

class DeploymentRecord(BaseModel):
    service_name: str
    version: str
    timestamp: str
    reason: Optional[str] = None
    risk_score: Optional[int] = None
    rollback_status: Optional[str] = None
