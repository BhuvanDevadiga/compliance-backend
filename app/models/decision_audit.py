from sqlalchemy import String, Float, Integer, Column, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class DecisionAudit(Base):
    __tablename__ = "decision_audit"
    id = Column(Integer, primary_key = True, index = True)
    tenant_id = Column(String, index = True)
    ml_probability = Column(Float)
    rule_score = Column(Float)
    hybrid_score = Column(Float)
    threshold_used = Column(Float)

    forecast_trend = Column(Float, nullable=True)
    forecast_peak = Column(Float, nullable=True)

    drift_value = Column(Float, nullable=True)
    drift_streak = Column(Integer)

    retrain_triggered = Column(Boolean, default=False)

    strategy_selected = Column(String)
    confidence_score = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())