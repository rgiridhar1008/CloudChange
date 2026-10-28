from pydantic import BaseModel
from typing import List, Optional

class HistoryRecord(BaseModel):
    id: int
    service: str
    version: str
    status: str
    timestamp: str
    health_status: Optional[str] = None
    reason: Optional[str] = None
