from sqlalchemy import Boolean, Column, Integer, Float, String, DateTime, Text
from sqlalchemy.sql import func
from app.db.base import Base


class TenantRiskState(Base):
    __tablename__ = "tenant_risk_state"

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String, index=True, unique=True)

    risk_score = Column(Float, default=0)
    risk_level = Column(String, default="normal")

    last_escalation_reason = Column(String, nullable=True)
    last_reason = Column(Text, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    quarantined = Column(Boolean, default=False)
    quarantine_reason = Column(String, nullable=True)
    quarantined_at = Column(DateTime, nullable=True)


