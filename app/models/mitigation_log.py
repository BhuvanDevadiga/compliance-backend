from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String,  Float

from app.db.base import Base


class MitigationLog(Base):
    __tablename__ = "mitigation_logs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, nullable=False)
    action = Column(String)
    prediction = Column(String)
    context = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    ml_probability = Column(Float, nullable=True)
    hybrid_score = Column(Float, nullable=True)
    rule_score = Column(Float, nullable=True)
    actual_escalated = Column(Integer, nullable=True) 
    confidence = Column(Float, nullable=True)
