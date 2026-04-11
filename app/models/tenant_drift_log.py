from sqlalchemy import String, Column, Float, Integer, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class TenantDriftLog(Base):
    __tablename__ = "tenant_drift_logs"

    id = Column(Integer, primary_key=True, index=True)

    tenant_id = Column(String, index=True)

    recent_avg = Column(Float)
    baseline_avg = Column(Float)
    drift_value = Column(Float)

    drift_streak = Column(Integer)

    model_version = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())