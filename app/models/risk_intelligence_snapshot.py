from datetime import datetime

from sqlalchemy import Column, DateTime, String

from app.db.base import Base


class RiskIntelligenceSnapshot(Base):
    __tablename__ = "risk_intelligence_snapshots"

    tenant_id = Column(String, primary_key=True)
    timestamp = Column(DateTime, primary_key=True, default=datetime.utcnow)
    trend = Column(String)
    volatility = Column(String)
    interpretation = Column(String)


# Backward-compatible alias for older imports
RiskintelligenceSnapshot = RiskIntelligenceSnapshot
