from sqlalchemy import String, Integer, Column, Float, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class RiskHistory(Base):
    __tablename__ = "risk_history"
    id = Column(Integer, primary_key = True, index = True)
    tenant_id = Column(String, index = True)
    probability = Column(Float)
    velocity = Column(Float)
    stability = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
