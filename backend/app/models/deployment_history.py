from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base
from datetime import datetime, timezone

class DeploymentHistory(Base):
    __tablename__ = "deployment_history"

    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String, index=True)
    version = Column(String)
    status = Column(String)
    health_status = Column(String)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    reason = Column(String, nullable=True)
