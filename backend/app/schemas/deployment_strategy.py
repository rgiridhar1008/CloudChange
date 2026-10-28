from pydantic import BaseModel
from typing import List, Optional, Any, Union
from app.schemas.risk_analysis import BlastRadius

class RecommendationRequest(BaseModel):
    risk_score: int
    risk_level: str
    blast_radius: Union[dict, BlastRadius, Any]  # Allow dictionary or BlastRadius
    affected_services: List[str]
    criticality: str

class RecommendationResponse(BaseModel):
    strategy: str
    initial_percentage: int
    requires_approval: bool
    reason: str
    explanation: Optional[str] = None
