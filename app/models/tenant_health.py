from sqlalchemy import Float, String, Integer, Column, DateTime
from datetime import datetime
from app.db.base import Base

class TenantHealthSnapshot(Base):
    __tablename__ = "tenant_health_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True)
    health_index = Column(Float)
    drift_value = Column(Float)
    confidence_score = Column(Float)
    volatility_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)