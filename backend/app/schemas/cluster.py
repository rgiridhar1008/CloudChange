from pydantic import BaseModel
from typing import Optional, List

class ClusterHealthResponse(BaseModel):
    cluster: str
    status: str
    nodes: Optional[int] = None
    ready_nodes: Optional[int] = None
    timestamp: Optional[str] = None

class ServiceInfo(BaseModel):
    name: str
    namespace: str
    type: str = "Deployment"
    status: str
    replicas: int
    ready_replicas: int

class ServiceListResponse(BaseModel):
    services: List[ServiceInfo]
