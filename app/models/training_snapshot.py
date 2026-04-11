from sqlalchemy import Column, String, DateTime, Integer, Float
from app.db.base import Base
from datetime import datetime

class TrainingSnapshot(Base):
    __tablename__ = "training_snapshots"
    id = Column(Integer, primary_key = True, index = True)
    tenant_id = Column(String, index=True)

    velocity = Column(Float)
    stability = Column(Float)
    bias = Column(Float)
    forecast_peak = Column(Float)
    forecast_accuracy = Column(Float)
    adaptive_threshold = Column(Float)
    volatility = Column(Float)
    avg_strategy_confidence = Column(Float)
    long_term_success_ratio = Column(Float)
    short_term_success_ratio = Column(Float)

    escalated = Column(Integer)  # 1 = escalation happened, 0 = no escalation

    created_at = Column(DateTime, default=datetime.utcnow)