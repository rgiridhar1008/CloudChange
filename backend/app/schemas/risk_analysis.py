from pydantic import BaseModel, Field
from typing import List, Optional
from app.schemas.change_detection import ChangeItem
from app.schemas.dependency_analysis import ImpactResponse

class RiskFactor(BaseModel):
    factor: str
    score: int
    reason: str

class BlastRadius(BaseModel):
    affected_services_count: int
    affected_pods_count: int
    dependency_depth: int
    criticality: str
    traffic_exposure: str

class RiskRequest(BaseModel):
    changed_resource: str
    changes: List[ChangeItem]

class RiskResponse(BaseModel):
    risk_score: int
    risk_level: str
    risk_factors: List[RiskFactor]
    blast_radius: BlastRadius
    affected_services: List[str]
    affected_resources: List[str]
