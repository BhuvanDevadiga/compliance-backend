from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base

class DecisionFeedback(Base):
    __tablename__ = "decision_feedback"

    id = Column(Integer, primary_key=True, index=True)

    # Feedback references decision traces exposed by /api/risk/explain/{decision_id}.
    decision_id = Column(Integer, ForeignKey("decision_traces.id"))
    tenant_id = Column(String, index=True)

    outcome = Column(String)  
    # success | failure | false_positive

    reward = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
