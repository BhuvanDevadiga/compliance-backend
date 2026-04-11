import uuid
from sqlalchemy import String, Column, Float, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class AutonomousDecisionLog(Base):
    __tablename__ = "autonomous_decision_logs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, index=True, nullable=False)

    forecast_peak = Column(Float)
    forecast_accuracy = Column(Float)
    escalation_score = Column(Float)

    proactive_triggered = Column(Boolean)
    mitigation_level = Column(String)

    final_probability = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
                                            