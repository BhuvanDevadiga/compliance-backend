from sqlalchemy import ForeignKey, String, Column, Integer, Float, DateTime
from app.db.base import Base

class Control(Base):
    __tablename__ = "controls"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), nullable=False, index=True)

    name = Column(String, nullable=False)
    framework = Column(String, nullable=False)

    last_evidence_updated_at = Column(DateTime, nullable=True)
    owner_last_login = Column(DateTime, nullable=True)
    historical_failure_rate = Column(Float, default=0.0)
    next_audit_date = Column(DateTime, nullable=True)

    control_failure_prob = Column(Float, default=0.0, nullable=False)
    control_risk_level = Column(String(10), default="LOW", nullable=False)
    control_risk_updated_at = Column(DateTime, nullable=True)
                                     
                                       
