from sqlalchemy import Column, Integer, Float, String
from app.db.base import Base

class TenantBehaviorProfile(Base):
    __tablename__ = "tenant_behavior_profiles"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, unique=True, index=True)
    risk_score = Column(Float, default=0.0)
    escalation_bias = Column(Integer, default=0)
    stability_score = Column(Float, default=0.5)
    learning_confidence = Column(Float, default=1.0)