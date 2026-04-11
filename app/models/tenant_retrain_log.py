from sqlalchemy import String, Integer, Column, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class TenantRetrainLog(Base):
    __tablename__ = "tenant_retrain_logs"

    id = Column(Integer, primary_key=True, index=True)

    tenant_id = Column(String, index=True)

    old_version = Column(Integer)
    new_version = Column(Integer)

    reason = Column(String)  # drift / low_confidence / manual

    samples_used = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())