from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.base import Base

class EscalationFeedback(Base):
    __tablename__ = "escalation_feedback"
    id = Column(Integer, primary_key= True, index= True)
    tenant_id = Column(String, index=True, nullable=False)
    escalation_triggered = Column(Boolean, nullable=False)
    adaptive_threshold = Column(Integer, nullable=False)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)