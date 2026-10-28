from pydantic import BaseModel
from typing import Optional, Dict

class TrafficSplit(BaseModel):
    stable: int
    canary: int

class CurrentDeployment(BaseModel):
    service: str
    current_version: str
    target_version: str
    strategy: str
    traffic: TrafficSplit
    status: str
    health: str

class ClusterStatus(BaseModel):
    name: str
    status: str

class OverviewResponse(BaseModel):
    cluster: ClusterStatus
    active_deployments: int
    average_risk_score: int
    detected_changes: int
    current_deployment: Optional[CurrentDeployment] = None
