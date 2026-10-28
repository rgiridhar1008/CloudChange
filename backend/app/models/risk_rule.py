from sqlalchemy import Column, Integer, String
from app.core.database import Base

class RiskRule(Base):
    __tablename__ = "risk_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String, unique=True, index=True)
    change_type = Column(String)  # e.g., "REPLICA_REDUCTION", "MEMORY_REDUCTION", "REMOVED"
    path_keyword = Column(String, nullable=True) # e.g., "probe", "securitycontext"
    score = Column(Integer)
    reason_template = Column(String) # e.g., "Replicas reduced from {old} to {new}"
