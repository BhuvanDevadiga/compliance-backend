from sqlalchemy import Column, Integer, String, Float, JSON, DateTime
from datetime import datetime
from app.db.base import Base


class TenantProfile(Base):
    __tablename__ = "tenant_profiles"

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String, index=True)

    avg_risk_score = Column(Float)
    request_rate = Column(Float)

    endpoint_distribution = Column(JSON)
    avg_latency_ms = Column(Float)
    error_ratio = Column(Float, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    adaptive_threshold = Column(Float, default=0.55)
