from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.db.base import Base

class DecisionTrace(Base):
    __tablename__ = "decision_traces"
    id = Column(Integer, primary_key = True, index = True)
    tenant_id = Column(String, index = True)
    probability = Column(Float)
    hybrid_score = Column(Float)
    health_index = Column(Float)
    accuracy = Column(Float)
    pre_mitigation = Column(String)
    final_mitigation = Column(String)

    threshold_used = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)
    drift_value = Column(Float, nullable=True)
    forecast_state = Column(String, nullable=True)
    bandit_confidence = Column(Float, nullable=True)
