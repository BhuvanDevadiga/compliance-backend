from sqlalchemy import Column, String, Integer, Float, DateTime
from datetime import datetime
from app.db.base import Base

class ComplianceIncident(Base):
    __tablename__ = "compliance_incidents"

    id = Column(Integer, primary_key=True, index=True)

    tenant_id = Column(String, index=True)
    incident_type = Column(String)

    severity = Column(String)

    health_delta = Column(Float)
    strict_ratio = Column(Float)
    governance_delta = Column(Float)

    detected_at = Column(DateTime, default=datetime.utcnow)