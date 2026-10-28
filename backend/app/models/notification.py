from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime, timezone
from app.core.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, nullable=False)
    type = Column(String, nullable=False, default="INFO")
    read = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
