from pydantic import BaseModel
from typing import Optional

class StartDeploymentRequest(BaseModel):
    service_name: str
    new_version: str

class PromoteDeploymentRequest(BaseModel):
    service_name: str

class StopDeploymentRequest(BaseModel):
    service_name: str

class TrafficSplit(BaseModel):
    stable: int
    canary: int

class DeploymentEvent(BaseModel):
    event: str
    timestamp: str
    status: str

class DeploymentStatusResponse(BaseModel):
    service: str
    status: str
    strategy: str
    current_version: str
    target_version: str
    traffic: TrafficSplit
    health: str
    events: list[DeploymentEvent]
    # For backward compatibility during migration
    service_name: Optional[str] = None
    current_percentage: Optional[int] = None
    health_status: Optional[str] = None
    message: Optional[str] = None
