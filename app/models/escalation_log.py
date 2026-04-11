from sqlalchemy import String, Integer, Column, Float, DateTime
from datetime import datetime
from app.db.base import Base

class EscalationLog(Base):
    __tablename__ = "escalation_logs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True)

    escalation_signal = Column(String)
    recommended_action = Column(String)

    trend_slope = Column(Float)
    forecast_avg = Column(Float)
    expected_peak = Column(Float)

    model_version = Column(Integer)

    timestamp = Column(DateTime, default=datetime.utcnow)
    severity_score = Column(Float, nullable=True)

    