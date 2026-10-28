from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class ChangeItem(BaseModel):
    type: str = Field(..., description="The type of change (e.g., REPLICA_REDUCTION, MEMORY_INCREASE, MODIFIED, ADDED, REMOVED)")
    path: str = Field(..., description="The dot-notated path to the changed configuration key")
    old: Any = Field(None, description="The old value (if applicable)")
    new: Any = Field(None, description="The new value (if applicable)")

class ChangeRequest(BaseModel):
    old_config: Dict[str, Any] = Field(..., description="The previous configuration payload")
    new_config: Dict[str, Any] = Field(..., description="The proposed new configuration payload")

class ChangeResponse(BaseModel):
    changes: List[ChangeItem] = Field(..., description="A list of detected changes")
