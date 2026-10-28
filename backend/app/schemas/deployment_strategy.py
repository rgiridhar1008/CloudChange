from pydantic import BaseModel
from typing import List, Optional

class RecommendationRequest(BaseModel):
    risk_score: int
    risk_level: str
    blast_radius: dict  # Allow dictionary since it's nested
    affected_services: List[str]
    criticality: str

class RecommendationResponse(BaseModel):
    strategy: str
    initial_percentage: int
    requires_approval: bool
    reason: str
    explanation: Optional[str] = None
